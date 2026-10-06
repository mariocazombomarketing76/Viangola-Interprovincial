from datetime import date
from decimal import Decimal

from sqlalchemy import select

from .db import SessionLocal
from .models import Booking, Driver, Payment, Trip, TripSeat, User, Vehicle


def seed() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.email == "admin@viangola.ao")):
            return
        admin = User(full_name="Admin Viangola", email="admin@viangola.ao", role="admin", status="active")
        passenger = User(full_name="Maria da Silva", email="maria@viangola.ao", role="passenger", status="active")
        driver_user = User(full_name="Carlos Manuel", phone="+244923000001", role="driver", status="active")
        db.add_all([admin, passenger, driver_user])
        db.flush()
        driver = Driver(user_id=driver_user.id, bi_number="000000000LA000", approval_status="approved", approved_by=admin.id)
        db.add(driver)
        db.flush()
        vehicle = Vehicle(driver_id=driver.id, brand="Toyota", model="Coaster", year=2022, color="Branco", plate_number="LD-45-67-BX", seat_capacity=28, approval_status="approved")
        db.add(vehicle)
        db.flush()
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
        booking = Booking(trip_id=trips[0].id, passenger_id=passenger.id, seat_number="A4", amount=trips[0].price, status="paid")
        db.add(booking)
        db.flush()
        db.add(Payment(booking_id=booking.id, reference_number=f"VNG-{booking.id}-2026", payment_method="Multicaixa Express", amount=booking.amount, status="confirmed"))
        db.scalar(select(TripSeat).where(TripSeat.trip_id == trips[0].id, TripSeat.seat_number == "A4")).seat_status = "paid"
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()