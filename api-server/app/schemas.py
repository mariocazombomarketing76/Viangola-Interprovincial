from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --------------------------- Autenticação ---------------------------

class RegisterInput(BaseModel):
    fullName: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = Field(default=None, max_length=40)
    role: Literal["passenger", "driver"] = "passenger"


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshInput(BaseModel):
    refreshToken: str


class LogoutInput(BaseModel):
    refreshToken: str | None = None


class UserOut(BaseModel):
    id: int
    fullName: str
    email: str | None
    phone: str | None
    role: str
    isActive: bool
    createdAt: datetime
    lastLogin: datetime | None


class TokenOut(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    expiresIn: int
    user: UserOut


class AuthStatus(BaseModel):
    status: str


# ----------------------------- Viagens ------------------------------

class TripInput(BaseModel):
    origin: str
    destination: str
    departureDate: date
    departureTime: str
    price: float
    totalSeats: int


class BookingInput(BaseModel):
    tripId: int
    passengerName: str
    seatNumber: str


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    origin: str
    destination: str
    departureDate: date
    departureTime: str
    arrivalEstimate: str | None
    price: float
    availableSeats: int
    totalSeats: int
    status: str
    distance: float | None
    duration: int | None
    driverName: str
    vehicleLabel: str


class SeatOut(BaseModel):
    id: int
    tripId: int
    seatNumber: str
    seatStatus: str
    passengerName: str | None


class BookingOut(BaseModel):
    id: int
    tripId: int
    passengerName: str
    origin: str
    destination: str
    seatNumber: str
    amount: float
    status: str
    bookingDate: datetime


class PaymentOut(BaseModel):
    id: int
    bookingId: int
    referenceNumber: str
    paymentMethod: str
    amount: float
    status: str
    createdAt: datetime
    passengerName: str