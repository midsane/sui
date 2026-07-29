"""Add execution_sessions table

Revision ID: 002_add_execution_sessions
Revises: 8ba351a854ca
Create Date: 2026-07-29 20:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "002_add_execution_sessions"
down_revision = "8ba351a854ca"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "execution_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "paused",
                "completed",
                "failed",
                "cancelled",
                name="executionstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "requirements",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "plan", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "current_step_index", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "outputs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_execution_sessions_user_id"),
        "execution_sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_execution_sessions_status"),
        "execution_sessions",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_execution_sessions_status"), table_name="execution_sessions"
    )
    op.drop_index(
        op.f("ix_execution_sessions_user_id"), table_name="execution_sessions"
    )
    op.drop_table("execution_sessions")
