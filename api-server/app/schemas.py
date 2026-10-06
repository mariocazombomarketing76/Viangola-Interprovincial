from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


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