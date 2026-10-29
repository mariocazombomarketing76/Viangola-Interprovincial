"""Sprint 2 — testes de autenticação, sessões, perfis e proteção de rotas."""

import uuid

import pytest

from app.auth import hash_password
from app.db import SessionLocal
from app.models import Booking, Driver, Trip, User

STRONG_PASSWORD = "SenhaForte123"


def unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.ao"


def auth_header(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['accessToken']}"}


def login(client, email: str, password: str) -> dict:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def register_account(client, prefix: str, role: str = "passenger", password: str = STRONG_PASSWORD, phone: str | None = None):
    payload = {"fullName": f"Utilizador {prefix.title()}", "email": unique_email(prefix), "password": password, "role": role}
    if phone:
        payload["phone"] = phone
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json(), payload


@pytest.fixture
def passenger(client):
    tokens, payload = register_account(client, "passageiro")
    return {**tokens, "email": payload["email"]}


@pytest.fixture
def other_passenger(client):
    tokens, payload = register_account(client, "colega")
    return {**tokens, "email": payload["email"]}


@pytest.fixture
def driver_tokens(client):
    tokens, payload = register_account(client, "motorista", role="driver")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == payload["email"]).one()
        db.add(Driver(user_id=user.id, approval_status="approved"))
        db.commit()
    finally:
        db.close()
    return {**tokens, "email": payload["email"]}


@pytest.fixture
def admin(client):
    """Admin não é auto-registável — é criado diretamente (vem do seed em dev)."""
    email = unique_email("admin")
    db = SessionLocal()
    try:
        db.add(User(full_name="Admin Teste", email=email, password_hash=hash_password(STRONG_PASSWORD), role="admin", status="active", is_active=True))
        db.commit()
    finally:
        db.close()
    return {**login(client, email, STRONG_PASSWORD), "email": email}


def create_trip(client, admin_tokens: dict) -> dict:
    response = client.post(
        "/api/trips",
        json={"origin": "Luanda", "destination": "Benguela", "departureDate": "2026-09-01", "departureTime": "07:00", "price": 15000, "totalSeats": 12},
        headers=auth_header(admin_tokens),
    )
    assert response.status_code == 201, response.text
    return response.json()


def attach_driver_to_trip(trip_id: int, driver_email: str) -> None:
    db = SessionLocal()
    try:
        driver = db.query(Driver).join(User, Driver.user_id == User.id).filter(User.email == driver_email).one()
        trip = db.query(Trip).filter(Trip.id == trip_id).one()
        trip.driver_id = driver.id
        db.commit()
    finally:
        db.close()


# ------------------------------- Registo -------------------------------


def test_register_returns_tokens_and_user(client):
    tokens, payload = register_account(client, "registo")
    assert tokens["tokenType"] == "bearer"
    assert tokens["expiresIn"] > 0
    assert tokens["accessToken"] and tokens["refreshToken"]
    assert tokens["user"]["email"] == payload["email"]
    assert tokens["user"]["role"] == "passenger"
    assert tokens["user"]["isActive"] is True


def test_register_duplicate_email_conflict(client):
    _, payload = register_account(client, "duplicado")
    response = client.post("/api/auth/register", json={"fullName": "Outra Pessoa", "email": payload["email"], "password": STRONG_PASSWORD})
    assert response.status_code == 409


def test_register_duplicate_phone_conflict(client):
    _, payload = register_account(client, "telefone", phone="+244911000111")
    response = client.post("/api/auth/register", json={"fullName": "Outra Pessoa", "email": unique_email("telefone2"), "password": STRONG_PASSWORD, "phone": "+244911000111"})
    assert response.status_code == 409


def test_register_weak_password_rejected(client):
    response = client.post("/api/auth/register", json={"fullName": "Senha Curta", "email": unique_email("fraca"), "password": "1234567", "role": "passenger"})
    assert response.status_code == 422


def test_register_rejects_admin_self_registration(client):
    response = client.post("/api/auth/register", json={"fullName": "Super Admin", "email": unique_email("root"), "password": STRONG_PASSWORD, "role": "admin"})
    assert response.status_code == 422


def test_password_never_stored_in_plaintext(client, passenger):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == passenger["email"]).one()
        assert user.password_hash != STRONG_PASSWORD
        assert user.password_hash.startswith("$2")
    finally:
        db.close()


# ------------------------------- Login ---------------------------------


def test_login_success(client, passenger):
    profile = client.get("/api/auth/me", headers=auth_header(passenger))
    assert profile.status_code == 200
    assert profile.json()["email"] == passenger["email"]


def test_login_wrong_password_and_unknown_email(client):
    _, payload = register_account(client, "entrar")
    wrong = client.post("/api/auth/login", json={"email": payload["email"], "password": "PasswordErrada1"})
    assert wrong.status_code == 401
    unknown = client.post("/api/auth/login", json={"email": unique_email("fantasma"), "password": STRONG_PASSWORD})
    assert unknown.status_code == 401


def test_me_requires_authentication(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer token-falso"}).status_code == 401


# ------------------------------- Sessões --------------------------------


def test_refresh_rotates_tokens(client, passenger):
    reused = client.post("/api/auth/refresh", json={"refreshToken": passenger["refreshToken"]})
    assert reused.status_code == 200
    rotated = reused.json()
    assert rotated["accessToken"] and rotated["refreshToken"]
    assert rotated["refreshToken"] != passenger["refreshToken"]
    # o refresh antigo foi revogado — reutilização é rejeitada
    replay = client.post("/api/auth/refresh", json={"refreshToken": passenger["refreshToken"]})
    assert replay.status_code == 401


def test_logout_revokes_refresh_token(client, passenger):
    response = client.post("/api/auth/logout", json={"refreshToken": passenger["refreshToken"]})
    assert response.status_code == 200
    assert response.json()["status"] == "logged_out"
    after = client.post("/api/auth/refresh", json={"refreshToken": passenger["refreshToken"]})
    assert after.status_code == 401


# --------------------------- Proteção de rotas ---------------------------


def test_dashboard_requires_admin(client, passenger):
    assert client.get("/api/dashboard").status_code == 401
    assert client.get("/api/dashboard", headers=auth_header(passenger)).status_code == 403


def test_trip_creation_requires_admin(client, admin, passenger, driver_tokens):
    body = {"origin": "Luanda", "destination": "Huambo", "departureDate": "2026-09-02", "departureTime": "08:00", "price": 12000, "totalSeats": 10}
    assert client.post("/api/trips", json=body).status_code == 401
    assert client.post("/api/trips", json=body, headers=auth_header(passenger)).status_code == 403
    assert client.post("/api/trips", json=body, headers=auth_header(driver_tokens)).status_code == 403
    assert client.post("/api/trips", json=body, headers=auth_header(admin)).status_code == 201


def test_payments_admin_only(client, admin, passenger):
    assert client.get("/api/payments").status_code == 401
    assert client.get("/api/payments", headers=auth_header(passenger)).status_code == 403
    assert client.get("/api/payments", headers=auth_header(admin)).status_code == 200
    assert client.post("/api/payments/1/confirm", headers=auth_header(passenger)).status_code == 403
    assert client.post("/api/payments/1/confirm", headers=auth_header(admin)).status_code in (200, 404)


def test_trips_remain_public_for_browsing(client):
    assert client.get("/api/trips").status_code == 200


def test_booking_requires_authentication(client):
    response = client.post("/api/bookings", json={"tripId": 1, "passengerName": "Anonimo", "seatNumber": "A1"})
    assert response.status_code == 401


def test_booking_only_for_passenger_role(client, admin, driver_tokens):
    body = {"tripId": 1, "passengerName": "Não Passageiro", "seatNumber": "A1"}
    assert client.post("/api/bookings", json=body, headers=auth_header(admin)).status_code == 403
    assert client.post("/api/bookings", json=body, headers=auth_header(driver_tokens)).status_code == 403


def test_booking_is_bound_to_logged_in_user(client, admin, passenger):
    trip = create_trip(client, admin)
    response = client.post("/api/bookings", json={"tripId": trip["id"], "passengerName": "Nome Inventado", "seatNumber": "A1"}, headers=auth_header(passenger))
    assert response.status_code == 201, response.text
    db = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == response.json()["id"]).one()
        owner = db.query(User).filter(User.email == passenger["email"]).one()
        assert booking.passenger_id == owner.id
    finally:
        db.close()


def test_bookings_scoped_by_role(client, admin, passenger, other_passenger, driver_tokens):
    trip = create_trip(client, admin)
    attach_driver_to_trip(trip["id"], driver_tokens["email"])
    assert client.post("/api/bookings", json={"tripId": trip["id"], "passengerName": "Um", "seatNumber": "A1"}, headers=auth_header(passenger)).status_code == 201
    assert client.post("/api/bookings", json={"tripId": trip["id"], "passengerName": "Dois", "seatNumber": "A2"}, headers=auth_header(other_passenger)).status_code == 201

    mine = client.get("/api/bookings", headers=auth_header(passenger)).json()
    assert [b["seatNumber"] for b in mine] == ["A1"]
    assert all(b["tripId"] == trip["id"] for b in mine)

    theirs = client.get("/api/bookings", headers=auth_header(driver_tokens)).json()
    assert sorted(b["seatNumber"] for b in theirs) == ["A1", "A2"]

    everything = client.get("/api/bookings", headers=auth_header(admin)).json()
    assert len(everything) >= 2

    # outro motorista (sem viagens) não vê nada
    other_driver, payload = register_account(client, "motorista2", role="driver")
    empty = client.get("/api/bookings", headers=auth_header(other_driver)).json()
    assert empty == []
