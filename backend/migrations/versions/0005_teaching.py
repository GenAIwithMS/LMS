"""Teaching: daily attendance by the class incharge, syllabus progress per section,
the daily diary, class tests with marks, the weekly timetable, and a section for
each assignment.

Nothing is deleted. The old per-subject attendance table stays as it is.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-04 14:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('daily_attendance',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('student_id', sa.BigInteger(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('marked_by', sa.BigInteger(), nullable=True),
    sa.Column('marked_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], name='fk_daily_attendance_section_id'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name='fk_daily_attendance_student_id'),
    sa.ForeignKeyConstraint(['marked_by'], ['teachers.id'], name='fk_daily_attendance_marked_by'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'date', name='uq_daily_attendance_student_date')
    )
    op.create_table('chapter_progress',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('chapter_id', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('planned_date', sa.Date(), nullable=True),
    sa.Column('started_on', sa.Date(), nullable=True),
    sa.Column('completed_on', sa.Date(), nullable=True),
    sa.Column('updated_by', sa.BigInteger(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], name='fk_chapter_progress_section_id'),
    sa.ForeignKeyConstraint(['chapter_id'], ['syllabus_chapters.id'], name='fk_chapter_progress_chapter_id'),
    sa.ForeignKeyConstraint(['updated_by'], ['teachers.id'], name='fk_chapter_progress_updated_by'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('section_id', 'chapter_id', name='uq_progress_section_chapter')
    )
    op.create_table('diary_entries',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.Column('teacher_id', sa.BigInteger(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('classwork', sa.Text(), nullable=True),
    sa.Column('homework', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], name='fk_diary_entries_section_id'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='fk_diary_entries_subject_id'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name='fk_diary_entries_teacher_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('section_id', 'subject_id', 'date', name='uq_diary_section_subject_date')
    )
    op.create_table('class_tests',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.Column('teacher_id', sa.BigInteger(), nullable=False),
    sa.Column('chapter_id', sa.BigInteger(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('total_marks', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], name='fk_class_tests_section_id'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='fk_class_tests_subject_id'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name='fk_class_tests_teacher_id'),
    sa.ForeignKeyConstraint(['chapter_id'], ['syllabus_chapters.id'], name='fk_class_tests_chapter_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('class_test_marks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('test_id', sa.BigInteger(), nullable=False),
    sa.Column('student_id', sa.BigInteger(), nullable=False),
    sa.Column('obtained_marks', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['class_tests.id'], name='fk_class_test_marks_test_id'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name='fk_class_test_marks_student_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('test_id', 'student_id', name='uq_test_mark_test_student')
    )
    op.create_table('timetable_periods',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('day', sa.Integer(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], name='fk_timetable_periods_section_id'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='fk_timetable_periods_subject_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('section_id', 'day', 'period', name='uq_timetable_section_day_period')
    )

    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('section_id', sa.BigInteger(), nullable=True))
        batch_op.create_foreign_key('fk_assignments_section_id', 'sections', ['section_id'], ['id'])


def downgrade():
    with op.batch_alter_table('assignments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_assignments_section_id', type_='foreignkey')
        batch_op.drop_column('section_id')

    op.drop_table('timetable_periods')
    op.drop_table('class_test_marks')
    op.drop_table('class_tests')
    op.drop_table('diary_entries')
    op.drop_table('chapter_progress')
    op.drop_table('daily_attendance')
