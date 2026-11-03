"""Add the generic Interview application status.

Revision ID: 8c31f2e6a9d4
Revises: 5af4f02a7991
Create Date: 2026-11-03
"""

from typing import Sequence, Union

from alembic import op


revision: str = "8c31f2e6a9d4"
down_revision: Union[str, Sequence[str], None] = "5af4f02a7991"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'Interview'")


def downgrade() -> None:
    # PostgreSQL cannot remove an enum label without recreating the enum type.
    # Keep the value in the database during downgrade; the application model
    # controls whether the value is accepted by the API.
    pass
