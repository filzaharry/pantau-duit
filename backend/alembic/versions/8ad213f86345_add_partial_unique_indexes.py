"""add_partial_unique_indexes

Revision ID: 8ad213f86345
Revises: d0ef27e79951
Create Date: 2026-09-12 13:32:53.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ad213f86345'
down_revision: Union[str, Sequence[str], None] = 'd0ef27e79951'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Partial unique index for System Categories (where tenant_id IS NULL)
    op.execute("""
        CREATE UNIQUE INDEX uq_categories_system 
        ON categories (LOWER(name), type) 
        WHERE tenant_id IS NULL;
    """)

    # 2. Partial unique index for Tenant Custom Categories (where tenant_id IS NOT NULL)
    op.execute("""
        CREATE UNIQUE INDEX uq_categories_tenant 
        ON categories (tenant_id, LOWER(name), type) 
        WHERE tenant_id IS NOT NULL;
    """)

    # 3. Partial unique index for System Roles (where tenant_id IS NULL)
    op.execute("""
        CREATE UNIQUE INDEX uq_roles_system 
        ON roles (slug) 
        WHERE tenant_id IS NULL;
    """)

    # 4. Partial unique index for Tenant Roles (where tenant_id IS NOT NULL)
    op.execute("""
        CREATE UNIQUE INDEX uq_roles_tenant 
        ON roles (tenant_id, slug) 
        WHERE tenant_id IS NOT NULL;
    """)

    # 5. Partial index for active transactions (excluding soft-deleted rows)
    op.execute("""
        CREATE INDEX idx_transactions_active 
        ON transactions (tenant_id, transaction_date DESC) 
        WHERE deleted_at IS NULL;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_transactions_active;")
    op.execute("DROP INDEX IF EXISTS uq_roles_tenant;")
    op.execute("DROP INDEX IF EXISTS uq_roles_system;")
    op.execute("DROP INDEX IF EXISTS uq_categories_tenant;")
    op.execute("DROP INDEX IF EXISTS uq_categories_system;")
