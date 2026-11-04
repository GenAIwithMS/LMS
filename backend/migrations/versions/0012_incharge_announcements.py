"""Class announcements: an announcement can be marked as posted by the section's class
incharge (shown in its own colour).

Revision ID: 0012
Revises: 0011
Create Date: 2026-11-05 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('announcements', schema=None) as batch_op:
        batch_op.add_column(sa.Column('from_incharge', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('announcements', schema=None) as batch_op:
        batch_op.drop_column('from_incharge')
