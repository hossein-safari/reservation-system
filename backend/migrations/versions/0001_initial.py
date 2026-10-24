"""Initial reservation schema; deliberately independent of current application models."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "customer", "admin", name="user_role", native_enum=False, create_constraint=True
            ),
            nullable=False,
        ),
    )
    op.create_table(
        "resources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )
    op.create_table(
        "slots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("resource_id", sa.Uuid(), sa.ForeignKey("resources.id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price_irr", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="ck_slot_interval"),
        sa.CheckConstraint("price_irr > 0", name="ck_slot_price"),
    )
    op.create_index("ix_slots_resource_id", "slots", ["resource_id"])
    op.create_index("ix_slots_starts_at", "slots", ["starts_at"])
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
        op.execute("""ALTER TABLE slots ADD CONSTRAINT ex_slots_no_overlap
            EXCLUDE USING gist (
                resource_id WITH =,
                tstzrange(starts_at, ends_at, '[)') WITH &&
            )""")
    op.create_table(
        "reservations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("slot_id", sa.Uuid(), sa.ForeignKey("slots.id"), nullable=False),
        sa.Column("amount_irr", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "confirmed",
                "cancelled",
                name="reservation_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_irr > 0", name="ck_reservation_amount"),
    )
    op.create_index("ix_reservations_user_id", "reservations", ["user_id"])
    op.create_index(
        "uq_active_reservation_slot",
        "reservations",
        ["slot_id"],
        unique=True,
        sqlite_where=sa.text("status IN ('pending', 'confirmed')"),
        postgresql_where=sa.text("status IN ('pending', 'confirmed')"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "reservation_id",
            sa.Uuid(),
            sa.ForeignKey("reservations.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("amount_irr", sa.BigInteger(), nullable=False),
        sa.Column("provider_reference", sa.String(160), nullable=False, unique=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "succeeded",
                name="payment_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_irr > 0", name="ck_payment_amount"),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "payment_id", sa.Uuid(), sa.ForeignKey("payments.id"), nullable=False, unique=True
        ),
        sa.Column("reference", sa.String(160), nullable=False, unique=True),
        sa.Column("amount_irr", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount_irr > 0", name="ck_transaction_amount"),
    )


def downgrade() -> None:
    for table in ("transactions", "payments", "reservations", "slots", "resources", "users"):
        op.drop_table(table)
