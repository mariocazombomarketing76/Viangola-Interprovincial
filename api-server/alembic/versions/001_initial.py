"""Initial Viangola persistence schema."""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("full_name", sa.String(160), nullable=False), sa.Column("phone", sa.String(40), unique=True), sa.Column("email", sa.String(255), unique=True), sa.Column("password_hash", sa.String(255)), sa.Column("role", sa.String(30), nullable=False, server_default="passenger"), sa.Column("status", sa.String(30), nullable=False, server_default="active"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("drivers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True), sa.Column("bi_number", sa.String(80)), sa.Column("selfie_photo", sa.Text()), sa.Column("driver_license", sa.Text()), sa.Column("driver_license_expiry", sa.Date()), sa.Column("approval_status", sa.String(30), nullable=False, server_default="pending"), sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("approved_at", sa.DateTime(timezone=True)))
    op.create_table("vehicles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("driver_id", sa.Integer(), sa.ForeignKey("drivers.id"), nullable=False), sa.Column("brand", sa.String(80), nullable=False), sa.Column("model", sa.String(80), nullable=False), sa.Column("year", sa.Integer()), sa.Column("color", sa.String(40)), sa.Column("plate_number", sa.String(30), unique=True, nullable=False), sa.Column("seat_capacity", sa.Integer(), nullable=False), sa.Column("vehicle_photo", sa.Text()), sa.Column("interprovincial_license", sa.Text()), sa.Column("approval_status", sa.String(30), nullable=False, server_default="approved"))
    op.create_table("trips", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("driver_id", sa.Integer(), sa.ForeignKey("drivers.id")), sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id")), sa.Column("origin", sa.String(100), nullable=False), sa.Column("destination", sa.String(100), nullable=False), sa.Column("departure_date", sa.Date(), nullable=False), sa.Column("departure_time", sa.String(10), nullable=False), sa.Column("arrival_estimate", sa.String(10)), sa.Column("price", sa.Numeric(12, 2), nullable=False), sa.Column("available_seats", sa.Integer(), nullable=False), sa.Column("total_seats", sa.Integer(), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="scheduled"), sa.Column("distance", sa.Numeric(10, 2)), sa.Column("duration", sa.Integer()))
    op.create_table("trip_seats", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False), sa.Column("seat_number", sa.String(10), nullable=False), sa.Column("seat_status", sa.String(30), nullable=False, server_default="available"), sa.Column("passenger_id", sa.Integer(), sa.ForeignKey("users.id")))
    op.create_table("bookings", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id"), nullable=False), sa.Column("passenger_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("seat_number", sa.String(10), nullable=False), sa.Column("amount", sa.Numeric(12, 2), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="pending"), sa.Column("booking_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("payments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id"), nullable=False), sa.Column("reference_number", sa.String(80), unique=True, nullable=False), sa.Column("payment_method", sa.String(60), nullable=False), sa.Column("proof_of_payment", sa.Text()), sa.Column("amount", sa.Numeric(12, 2), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="pending"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_trip_seats_trip_seat", "trip_seats", ["trip_id", "seat_number"], unique=True)
    op.create_index("ix_bookings_trip_seat", "bookings", ["trip_id", "seat_number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bookings_trip_seat", table_name="bookings")
    op.drop_index("ix_trip_seats_trip_seat", table_name="trip_seats")
    op.drop_table("payments")
    op.drop_table("bookings")
    op.drop_table("trip_seats")
    op.drop_table("trips")
    op.drop_table("vehicles")
    op.drop_table("drivers")
    op.drop_table("users")