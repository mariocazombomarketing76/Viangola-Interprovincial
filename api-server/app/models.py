from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), unique=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="passenger")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    driver: Mapped["Driver | None"] = relationship(back_populates="user", foreign_keys="Driver.user_id")


class Driver(Base):
    __tablename__ = "drivers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    bi_number: Mapped[str | None] = mapped_column(String(80))
    selfie_photo: Mapped[str | None] = mapped_column(Text)
    driver_license: Mapped[str | None] = mapped_column(Text)
    driver_license_expiry: Mapped[date | None] = mapped_column(Date)
    approval_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="driver", foreign_keys=[user_id])
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="driver")
    trips: Mapped[list["Trip"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    color: Mapped[str | None] = mapped_column(String(40))
    plate_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    seat_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicle_photo: Mapped[str | None] = mapped_column(Text)
    interprovincial_license: Mapped[str | None] = mapped_column(Text)
    approval_status: Mapped[str] = mapped_column(String(30), nullable=False, default="approved")
    driver: Mapped[Driver] = relationship(back_populates="vehicles")
    trips: Mapped[list["Trip"]] = relationship(back_populates="vehicle")


class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"))
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicles.id"))
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    departure_time: Mapped[str] = mapped_column(String(10), nullable=False)
    arrival_estimate: Mapped[str | None] = mapped_column(String(10))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled")
    distance: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    duration: Mapped[int | None] = mapped_column(Integer)
    driver: Mapped[Driver | None] = relationship(back_populates="trips")
    vehicle: Mapped[Vehicle | None] = relationship(back_populates="trips")
    seats: Mapped[list["TripSeat"]] = relationship(back_populates="trip", cascade="all, delete-orphan")


class TripSeat(Base):
    __tablename__ = "trip_seats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    seat_status: Mapped[str] = mapped_column(String(30), nullable=False, default="available")
    passenger_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    trip: Mapped[Trip] = relationship(back_populates="seats")


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    passenger_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    booking_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    passenger: Mapped[User | None] = relationship()
    trip: Mapped[Trip] = relationship()


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(60), nullable=False)
    proof_of_payment: Mapped[str | None] = mapped_column(Text)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    booking: Mapped[Booking] = relationship()