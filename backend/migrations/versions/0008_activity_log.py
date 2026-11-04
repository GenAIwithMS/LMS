"""Activity log: who did what, when and from where (every change, login and logout).

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-04 22:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('activity_logs',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_role', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('user_name', sa.String(length=255), nullable=True),
    sa.Column('action', sa.String(length=20), nullable=False),
    sa.Column('area', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('method', sa.String(length=10), nullable=False),
    sa.Column('path', sa.String(length=255), nullable=False),
    sa.Column('ip_address', sa.String(length=64), nullable=True),
    sa.Column('status_code', sa.Integer(), nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=True),
    sa.Column('class_id', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])
    op.create_index('ix_activity_logs_user', 'activity_logs', ['user_role', 'user_id'])


def downgrade():
    op.drop_index('ix_activity_logs_user', table_name='activity_logs')
    op.drop_index('ix_activity_logs_created_at', table_name='activity_logs')
    op.drop_table('activity_logs')
