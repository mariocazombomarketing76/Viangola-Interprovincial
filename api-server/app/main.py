from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .auth import (
    create_access_token,
    get_current_user,
    hash_password,
    issue_refresh_token,
    require_roles,
    revoke_refresh_token,
    validate_refresh_token,
    verify_password,
)
from .db import get_db
from .models import Booking, Driver, Payment, RefreshToken, Trip, TripSeat, User, Vehicle
from .schemas import (
    AuthStatus,
    BookingInput,
    BookingOut,
    LoginInput,
    LogoutInput,
    PaymentOut,
    RefreshInput,
    RegisterInput,
    SeatOut,
    TokenOut,
    TripInput,
    TripOut,
    UserOut,
)

app = FastAPI(title="Viangola Interprovincial API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def trip_out(trip: Trip) -> TripOut:
    return TripOut(
        id=trip.id, origin=trip.origin, destination=trip.destination, departureDate=trip.departure_date,
        departureTime=trip.departure_time, arrivalEstimate=trip.arrival_estimate, price=float(trip.price),
        availableSeats=trip.available_seats, totalSeats=trip.total_seats, status=trip.status,
        distance=float(trip.distance) if trip.distance is not None else None, duration=trip.duration,
        driverName=trip.driver.user.full_name if trip.driver and trip.driver.user else "A atribuir",
        vehicleLabel=f"{trip.vehicle.brand} {trip.vehicle.model} · {trip.vehicle.plate_number}" if trip.vehicle else "A atribuir",
    )


def booking_out(booking: Booking) -> BookingOut:
    return BookingOut(
        id=booking.id, tripId=booking.trip_id, passengerName=booking.passenger.full_name if booking.passenger else "Passageiro",
        origin=booking.trip.origin, destination=booking.trip.destination, seatNumber=booking.seat_number,
        amount=float(booking.amount), status=booking.status, bookingDate=booking.booking_date,
    )


def payment_out(payment: Payment) -> PaymentOut:
    booking = payment.booking
    return PaymentOut(
        id=payment.id, bookingId=payment.booking_id, referenceNumber=payment.reference_number,
        paymentMethod=payment.payment_method, amount=float(payment.amount), status=payment.status,
        createdAt=payment.created_at, passengerName=booking.passenger.full_name if booking and booking.passenger else "Passageiro",
    )


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        fullName=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        isActive=user.is_active,
        createdAt=user.created_at,
        lastLogin=user.last_login,
    )


def issue_tokens(db: Session, user: User) -> TokenOut:
    access_token, expires_in = create_access_token(user)
    refresh_token = issue_refresh_token(db, user)
    return TokenOut(
        accessToken=access_token,
        refreshToken=refresh_token,
        tokenType="bearer",
        expiresIn=expires_in,
        user=user_out(user),
    )


@app.get("/api/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


# ----------------------------- Autenticação -----------------------------


@app.post("/api/auth/register", response_model=TokenOut, status_code=201)
def register(body: RegisterInput, db: Session = Depends(get_db)) -> TokenOut:
    email = body.email.lower().strip()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(409, "Email já registado")
    if body.phone and db.scalar(select(User.id).where(User.phone == body.phone)):
        raise HTTPException(409, "Telefone já registado")
    now = datetime.now(timezone.utc)
    user = User(
        full_name=body.fullName.strip(),
        email=email,
        phone=body.phone,
        password_hash=hash_password(body.password),
        role=body.role,
        status="active",
        is_active=True,
        created_at=now,
        updated_at=now,
        last_login=now,
    )
    db.add(user)
    db.flush()
    tokens = issue_tokens(db, user)
    db.commit()
    return tokens


@app.post("/api/auth/login", response_model=TokenOut)
def login(body: LoginInput, db: Session = Depends(get_db)) -> TokenOut:
    email = body.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Credenciais inválidas")
    if not user.is_active:
        raise HTTPException(401, "Conta desativada")
    user.last_login = datetime.now(timezone.utc)
    tokens = issue_tokens(db, user)
    db.commit()
    return tokens


@app.post("/api/auth/refresh", response_model=TokenOut)
def refresh_session(body: RefreshInput, db: Session = Depends(get_db)) -> TokenOut:
    user, jti = validate_refresh_token(db, body.refreshToken)
    row = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)
        db.add(row)
    tokens = issue_tokens(db, user)
    db.commit()
    return tokens


@app.post("/api/auth/logout", response_model=AuthStatus)
def logout(body: LogoutInput, db: Session = Depends(get_db)) -> AuthStatus:
    if body.refreshToken:
        revoke_refresh_token(db, body.refreshToken)
        db.commit()
    return AuthStatus(status="logged_out")


@app.get("/api/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return user_out(user)


@app.get("/api/dashboard")
def dashboard(admin: User = Depends(require_roles("admin")), db: Session = Depends(get_db)) -> dict:
    paid = db.scalars(select(Booking).where(Booking.status == "paid")).all()
    today = datetime.now(timezone.utc).date()
    paid_by_day = {}
    for booking in paid:
        booking_day = booking.booking_date.date()
        if today - timedelta(days=6) <= booking_day <= today:
            paid_by_day[booking_day] = paid_by_day.get(booking_day, Decimal("0")) + booking.amount
    weekly_revenue = [
        {
            "day": (today - timedelta(days=offset)).strftime("%a"),
            "amount": float(paid_by_day.get(today - timedelta(days=offset), Decimal("0"))),
        }
        for offset in range(6, -1, -1)
    ]
    return {
        "revenue": float(sum((booking.amount for booking in paid), Decimal("0"))),
        "revenueChange": 12.4,
        "bookings": db.scalar(select(func.count(Booking.id))) or 0,
        "activeDrivers": db.scalar(select(func.count(Driver.id)).where(Driver.approval_status == "approved")) or 0,
        "completedTrips": db.scalar(select(func.count(Trip.id)).where(Trip.status == "completed")) or 0,
        "passengers": db.scalar(select(func.count(User.id)).where(User.role == "passenger")) or 0,
        "weeklyRevenue": weekly_revenue,
        "recentBookings": [booking_out(item) for item in db.scalars(select(Booking).options(joinedload(Booking.trip), joinedload(Booking.passenger)).order_by(Booking.booking_date.desc()).limit(4)).all()],
    }


@app.get("/api/trips", response_model=list[TripOut])
def list_trips(origin: str | None = None, destination: str | None = None, date: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = select(Trip).options(joinedload(Trip.driver).joinedload(Driver.user), joinedload(Trip.vehicle)).order_by(Trip.departure_date, Trip.departure_time)
    if origin: query = query.where(Trip.origin.ilike(f"%{origin}%"))
    if destination: query = query.where(Trip.destination.ilike(f"%{destination}%"))
    if date: query = query.where(Trip.departure_date == date)
    if status: query = query.where(Trip.status == status)
    return [trip_out(item) for item in db.scalars(query).all()]


@app.post("/api/trips", response_model=TripOut, status_code=201)
def create_trip(body: TripInput, admin: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    trip = Trip(origin=body.origin, destination=body.destination, departure_date=body.departureDate, departure_time=body.departureTime, price=body.price, available_seats=body.totalSeats, total_seats=body.totalSeats, status="scheduled")
    db.add(trip)
    db.flush()
    db.add_all([TripSeat(trip_id=trip.id, seat_number=f"{chr(65 + index // 4)}{index % 4 + 1}") for index in range(body.totalSeats)])
    db.commit()
    db.refresh(trip)
    return trip_out(trip)


@app.get("/api/trips/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.scalar(select(Trip).options(joinedload(Trip.driver).joinedload(Driver.user), joinedload(Trip.vehicle)).where(Trip.id == trip_id))
    if not trip: raise HTTPException(404, "Viagem não encontrada")
    return trip_out(trip)


@app.get("/api/trips/{trip_id}/seats", response_model=list[SeatOut])
def get_trip_seats(trip_id: int, db: Session = Depends(get_db)):
    seats = db.scalars(select(TripSeat).options(joinedload(TripSeat.trip)).where(TripSeat.trip_id == trip_id).order_by(TripSeat.id)).all()
    bookings = db.scalars(select(Booking).options(joinedload(Booking.passenger)).where(Booking.trip_id == trip_id, Booking.status != "cancelled")).all()
    by_seat = {booking.seat_number: booking for booking in bookings}
    return [SeatOut(id=seat.id, tripId=seat.trip_id, seatNumber=seat.seat_number, seatStatus=by_seat[seat.seat_number].status if seat.seat_number in by_seat else "available", passengerName=by_seat[seat.seat_number].passenger.full_name if seat.seat_number in by_seat and by_seat[seat.seat_number].passenger else None) for seat in seats]


@app.get("/api/bookings", response_model=list[BookingOut])
def list_bookings(status: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Booking).options(joinedload(Booking.trip), joinedload(Booking.passenger)).order_by(Booking.booking_date.desc())
    # Ámbito por papel: admin vê tudo; motorista vê reservas das suas viagens;
    # passageiro vê apenas as suas.
    if user.role == "driver":
        driver_id = db.scalar(select(Driver.id).where(Driver.user_id == user.id))
        if driver_id is None:
            return []
        query = query.join(Booking.trip).where(Trip.driver_id == driver_id)
    elif user.role == "passenger":
        query = query.where(Booking.passenger_id == user.id)
    if status: query = query.where(Booking.status == status)
    return [booking_out(item) for item in db.scalars(query).all()]


@app.post("/api/bookings", response_model=BookingOut, status_code=201)
def create_booking(body: BookingInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> BookingOut:
    if user.role != "passenger":
        raise HTTPException(403, "Apenas passageiros podem reservar lugares")
    trip = db.scalar(select(Trip).where(Trip.id == body.tripId).with_for_update())
    if not trip: raise HTTPException(404, "Viagem não encontrada")
    seat = db.scalar(select(TripSeat).where(TripSeat.trip_id == trip.id, TripSeat.seat_number == body.seatNumber).with_for_update())
    if not seat or seat.seat_status != "available": raise HTTPException(409, "Este lugar já não está disponível")
    # A reserva fica sempre associada à conta autenticada (o nome do corpo é
    # apenas informativo e ignorado pelo servidor).
    booking = Booking(trip_id=trip.id, passenger_id=user.id, seat_number=seat.seat_number, amount=trip.price, status="pending", booking_date=datetime.now(timezone.utc))
    seat.seat_status = "reserved"
    trip.available_seats -= 1
    db.add(booking)
    db.flush()
    db.add(Payment(booking_id=booking.id, reference_number=f"VNG-{booking.id}-2026", payment_method="Multicaixa Express", amount=booking.amount, status="pending"))
    db.commit()
    db.refresh(booking)
    return booking_out(booking)


@app.get("/api/payments", response_model=list[PaymentOut])
def list_payments(admin: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return [payment_out(item) for item in db.scalars(select(Payment).options(joinedload(Payment.booking).joinedload(Booking.passenger)).order_by(Payment.created_at.desc())).all()]


@app.post("/api/payments/{payment_id}/confirm", response_model=PaymentOut)
def confirm_payment(payment_id: int, admin: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    payment = db.scalar(select(Payment).where(Payment.id == payment_id).with_for_update())
    if not payment: raise HTTPException(404, "Pagamento não encontrado")
    booking = db.scalar(select(Booking).where(Booking.id == payment.booking_id).with_for_update())
    if not booking: raise HTTPException(409, "Reserva associada não encontrada")
    booking.passenger = db.scalar(select(User).where(User.id == booking.passenger_id))
    payment.booking = booking
    payment.status = "confirmed"
    booking.status = "paid"
    seat = db.scalar(select(TripSeat).where(TripSeat.trip_id == booking.trip_id, TripSeat.seat_number == booking.seat_number))
    if seat: seat.seat_status = "paid"
    db.commit()
    db.refresh(payment)
    return payment_out(payment)