"""create product_views

Revision ID: 0010
Revises: 0009
Create Date: 2026-01-01 00:09:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_views",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_product_views_product_id", "product_views", ["product_id"])
    op.create_index("ix_product_views_viewed_at", "product_views", ["viewed_at"])
    op.create_index("ix_product_views_product_viewed", "product_views", ["product_id", "viewed_at"])


def downgrade() -> None:
    op.drop_table("product_views")
