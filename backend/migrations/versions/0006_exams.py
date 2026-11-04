"""Exams: terms per session, papers per class and subject (with the question paper
file and the admin's review), marks per student, and the class incharge's
report card remarks.

Nothing is deleted. The old results table stays as it is.

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-04 18:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('exam_terms',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('session_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('marks_deadline', sa.Date(), nullable=True),
    sa.Column('is_locked', sa.Boolean(), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['academic_sessions.id'], name='fk_exam_terms_session_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id', 'name', name='uq_exam_term_session_name')
    )
    op.create_table('exam_papers',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('term_id', sa.BigInteger(), nullable=False),
    sa.Column('class_id', sa.BigInteger(), nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.Column('total_marks', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('passing_marks', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('exam_date', sa.Date(), nullable=True),
    sa.Column('question_file', sa.String(length=255), nullable=True),
    sa.Column('question_status', sa.String(length=20), nullable=False),
    sa.Column('review_note', sa.Text(), nullable=True),
    sa.Column('uploaded_by', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['term_id'], ['exam_terms.id'], name='fk_exam_papers_term_id'),
    sa.ForeignKeyConstraint(['class_id'], ['school_classes.id'], name='fk_exam_papers_class_id'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='fk_exam_papers_subject_id'),
    sa.ForeignKeyConstraint(['uploaded_by'], ['teachers.id'], name='fk_exam_papers_uploaded_by'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('term_id', 'subject_id', name='uq_exam_paper_term_subject')
    )
    op.create_table('exam_marks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('paper_id', sa.BigInteger(), nullable=False),
    sa.Column('student_id', sa.BigInteger(), nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('obtained_marks', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('is_absent', sa.Boolean(), nullable=False),
    sa.Column('entered_by', sa.BigInteger(), nullable=True),
    sa.Column('entered_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['paper_id'], ['exam_papers.id'], name='fk_exam_marks_paper_id'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name='fk_exam_marks_student_id'),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], name='fk_exam_marks_section_id'),
    sa.ForeignKeyConstraint(['entered_by'], ['teachers.id'], name='fk_exam_marks_entered_by'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('paper_id', 'student_id', name='uq_exam_mark_paper_student')
    )
    op.create_table('report_remarks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('term_id', sa.BigInteger(), nullable=False),
    sa.Column('student_id', sa.BigInteger(), nullable=False),
    sa.Column('remarks', sa.Text(), nullable=False),
    sa.Column('written_by', sa.BigInteger(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['term_id'], ['exam_terms.id'], name='fk_report_remarks_term_id'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name='fk_report_remarks_student_id'),
    sa.ForeignKeyConstraint(['written_by'], ['teachers.id'], name='fk_report_remarks_written_by'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('term_id', 'student_id', name='uq_report_remark_term_student')
    )


def downgrade():
    op.drop_table('report_remarks')
    op.drop_table('exam_marks')
    op.drop_table('exam_papers')
    op.drop_table('exam_terms')
