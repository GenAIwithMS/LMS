"""Announcements from the admin: an announcement's author can be the admin instead of a
teacher, and it can be for a whole class (every section of it).

Nothing is deleted; teachers' announcements stay as they are.

Revision ID: 0011
Revises: 0010
Create Date: 2026-11-05 14:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('announcements', schema=None) as batch_op:
        batch_op.alter_column('teacher_id', existing_type=sa.BigInteger(), nullable=True)
        batch_op.add_column(sa.Column('admin_id', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('class_id', sa.BigInteger(), nullable=True))
        batch_op.create_foreign_key('fk_announcements_admin_id', 'admin', ['admin_id'], ['id'])
        batch_op.create_foreign_key('fk_announcements_class_id', 'school_classes', ['class_id'], ['id'])


def downgrade():
    # Admin announcements have no teacher, so they can't fit the old table
    op.execute("DELETE FROM announcements WHERE teacher_id IS NULL")
    with op.batch_alter_table('announcements', schema=None) as batch_op:
        batch_op.drop_constraint('fk_announcements_class_id', type_='foreignkey')
        batch_op.drop_constraint('fk_announcements_admin_id', type_='foreignkey')
        batch_op.drop_column('class_id')
        batch_op.drop_column('admin_id')
        batch_op.alter_column('teacher_id', existing_type=sa.BigInteger(), nullable=False)
