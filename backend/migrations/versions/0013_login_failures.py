"""Wrong-password counts per account, kept in the database so every server process
shares them (login protection that works with several workers).

Revision ID: 0013
Revises: 0012
Create Date: 2026-11-05 18:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'login_failures',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_login_failures_email', 'login_failures', ['email'])
    op.create_index('ix_login_failures_failed_at', 'login_failures', ['failed_at'])


def downgrade():
    op.drop_index('ix_login_failures_failed_at', table_name='login_failures')
    op.drop_index('ix_login_failures_email', table_name='login_failures')
    op.drop_table('login_failures')
