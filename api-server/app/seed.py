"""Seed determinístico da Viangola Interprovincial.

Cria (e sempre que corre, ressincroniza) as três contas de demonstração,
o motorista, a viatura, as viagens e a reserva de exemplo.

Credenciais de teste (também documentadas no README.md):
    admin@viangola.ao     / Admin123!     (admin)
    driver@viangola.ao    / Driver123!    (motorista)
    maria@viangola.ao     / Passenger123! (passageiro)
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from .auth import hash_password
from .db import SessionLocal
from .models import Booking, Driver, Payment, Trip, TripSeat, User, Vehicle

SEED_ACCOUNTS = [
    {"full_name": "Admin Viangola", "email": "admin@viangola.ao", "phone": "+244923000000", "role": "admin", "password": "Admin123!"},
    {"full_name": "Carlos Manuel", "email": "driver@viangola.ao", "phone": "+244923000001", "role": "driver", "password": "Driver123!"},
    {"full_name": "Maria da Silva", "email": "maria@viangola.ao", "phone": "+244923000002", "role": "passenger", "password": "Passenger123!"},
]


def upsert_account(db, account: dict) -> User:
    """Cria ou atualiza uma conta de demonstração (procura por email OU telefone
    para também apanhar contas antigas criadas sem email)."""
    user = db.scalar(
        select(User).where((User.email == account["email"]) | (User.phone == account["phone"]))
    )
    if user is None:
        user = User(email=account["email"])
        db.add(user)
    user.full_name = account["full_name"]
    user.email = account["email"]
    user.phone = account["phone"]
    user.role = account["role"]
    user.status = "active"
    user.is_active = True
    user.password_hash = hash_password(account["password"])
    db.flush()
    return user


def seed() -> None:
    db = SessionLocal()
    try:
        # 1. Contas de demonstração (sempre com credenciais válidas).
        accounts = {account["role"]: upsert_account(db, account) for account in SEED_ACCOUNTS}
        admin, driver_user, passenger = accounts["admin"], accounts["driver"], accounts["passenger"]

        # 2. Motorista + viatura.
        driver = db.scalar(select(Driver).where(Driver.user_id == driver_user.id))
        if driver is None:
            driver = Driver(user_id=driver_user.id, bi_number="000000000LA000", approval_status="approved", approved_by=admin.id)
            db.add(driver)
            db.flush()
        vehicle = db.scalar(select(Vehicle).where(Vehicle.driver_id == driver.id))
        if vehicle is None:
            vehicle = Vehicle(driver_id=driver.id, brand="Toyota", model="Coaster", year=2022, color="Branco", plate_number="LD-45-67-BX", seat_capacity=28, approval_status="approved")
            db.add(vehicle)
            db.flush()

        # 3. Viagens + lugares (apenas se a base ainda não tiver viagens).
        if db.scalar(select(Trip.id).limit(1)) is None:
            trips = [
                Trip(driver_id=driver.id, vehicle_id=vehicle.id, origin="Luanda", destination="Benguela", departure_date=date(2026, 8, 24), departure_time="06:30", arrival_estimate="13:15", price=Decimal("18500"), available_seats=8, total_seats=28, status="scheduled", distance=Decimal("692"), duration=405),
                Trip(driver_id=driver.id, vehicle_id=vehicle.id, origin="Luanda", destination="Malanje", departure_date=date(2026, 8, 24), departure_time="07:00", arrival_estimate="12:40", price=Decimal("16000"), available_seats=14, total_seats=24, status="scheduled", distance=Decimal("423"), duration=340),
                Trip(driver_id=driver.id, vehicle_id=vehicle.id, origin="Benguela", destination="Lubango", departure_date=date(2026, 8, 25), departure_time="05:45", arrival_estimate="10:30", price=Decimal("12500"), available_seats=5, total_seats=20, status="boarding", distance=Decimal("338"), duration=285),
                Trip(driver_id=driver.id, vehicle_id=vehicle.id, origin="Luanda", destination="Uíge", departure_date=date(2026, 8, 26), departure_time="06:00", arrival_estimate="12:10", price=Decimal("17500"), available_seats=21, total_seats=28, status="scheduled", distance=Decimal("345"), duration=370),
            ]
            db.add_all(trips)
            db.flush()
            for trip in trips:
                db.add_all([TripSeat(trip_id=trip.id, seat_number=f"{chr(65 + index // 4)}{index % 4 + 1}") for index in range(trip.total_seats)])

        # 4. Reserva de exemplo (apenas se ainda não existir nenhuma).
        if db.scalar(select(Booking.id).limit(1)) is None:
            trip = db.scalar(select(Trip).order_by(Trip.id))
            seat = db.scalar(select(TripSeat).where(TripSeat.trip_id == trip.id, TripSeat.seat_number == "A4")) if trip else None
            if trip is not None and seat is not None:
                booking = Booking(trip_id=trip.id, passenger_id=passenger.id, seat_number=seat.seat_number, amount=trip.price, status="paid")
                db.add(booking)
                db.flush()
                db.add(Payment(booking_id=booking.id, reference_number=f"VNG-{booking.id}-2026", payment_method="Multicaixa Express", amount=booking.amount, status="confirmed"))
                seat.seat_status = "paid"
                trip.available_seats = max(trip.available_seats - 1, 0)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
