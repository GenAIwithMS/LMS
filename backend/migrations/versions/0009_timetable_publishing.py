"""Timetable: the bell schedule (period times and breaks), the school days, and
published timetables (what teachers and students see).

Starts with 8 periods of 40 minutes from 08:00, a break after period 4, Monday to Saturday.

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-05 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


DEFAULT_PERIODS = [
    ("Period 1", "08:00", "08:40", False),
    ("Period 2", "08:40", "09:20", False),
    ("Period 3", "09:20", "10:00", False),
    ("Period 4", "10:00", "10:40", False),
    ("Break", "10:40", "11:00", True),
    ("Period 5", "11:00", "11:40", False),
    ("Period 6", "11:40", "12:20", False),
    ("Period 7", "12:20", "13:00", False),
    ("Period 8", "13:00", "13:40", False),
]


def upgrade():
    op.create_table('school_periods',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('start_time', sa.String(length=5), nullable=False),
    sa.Column('end_time', sa.String(length=5), nullable=False),
    sa.Column('is_break', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number', name='uq_school_periods_number')
    )
    op.create_table('school_settings',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key', name='uq_school_settings_key')
    )
    op.create_table('timetable_versions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('published_at', sa.DateTime(), nullable=False),
    sa.Column('published_by', sa.String(length=255), nullable=True),
    sa.Column('days', sa.String(length=20), nullable=False),
    sa.Column('periods_json', sa.Text(), nullable=False),
    sa.Column('draft_signature', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('published_periods',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('version_id', sa.BigInteger(), nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('day', sa.Integer(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=True),
    sa.Column('subject_name', sa.String(length=255), nullable=False),
    sa.Column('teacher_id', sa.BigInteger(), nullable=True),
    sa.Column('teacher_name', sa.String(length=255), nullable=True),
    sa.Column('section_name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['version_id'], ['timetable_versions.id'], name='fk_published_periods_version_id'),
    sa.PrimaryKeyConstraint('id')
    )

    # The default bell schedule and school days
    school_periods = sa.table('school_periods', sa.column('id', sa.BigInteger), sa.column('number', sa.Integer),
                              sa.column('name', sa.String), sa.column('start_time', sa.String),
                              sa.column('end_time', sa.String), sa.column('is_break', sa.Boolean))
    rows = []
    number = 0
    for index, (name, start_time, end_time, is_break) in enumerate(DEFAULT_PERIODS):
        period_number = None
        if not is_break:
            number = number + 1
            period_number = number
        rows.append({"id": index + 1, "number": period_number, "name": name, "start_time": start_time,
                     "end_time": end_time, "is_break": is_break})
    op.bulk_insert(school_periods, rows)

    school_settings = sa.table('school_settings', sa.column('id', sa.BigInteger), sa.column('key', sa.String), sa.column('value', sa.Text))
    op.bulk_insert(school_settings, [{"id": 1, "key": "school_days", "value": "1,2,3,4,5,6"}])


def downgrade():
    op.drop_table('published_periods')
    op.drop_table('timetable_versions')
    op.drop_table('school_settings')
    op.drop_table('school_periods')
