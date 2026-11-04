"""School structure: sessions, Classes 1-10, sections with a class incharge,
subjects per class with chapters, and who teaches each subject in each section.

Nothing is deleted. Old sections and subjects stay as they are (without a class)
until the admin sets up the new structure.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-04 10:49:31.571625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('academic_sessions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('is_current', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('school_classes',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('level'),
    sa.UniqueConstraint('name')
    )

    # Classes 1 to 10 always exist
    school_classes = sa.table('school_classes', sa.column('id', sa.BigInteger), sa.column('name', sa.String), sa.column('level', sa.Integer))
    rows = []
    for level in range(1, 11):
        rows.append({"id": level, "name": f"Class {level}", "level": level})
    op.bulk_insert(school_classes, rows)

    op.create_table('syllabus_chapters',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subject_id', 'number', name='uq_chapter_subject_number')
    )
    op.create_table('teaching_assignments',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('section_id', sa.BigInteger(), nullable=False),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.Column('teacher_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('section_id', 'subject_id', name='uq_teaching_section_subject')
    )
    with op.batch_alter_table('sections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('class_id', sa.BigInteger(), nullable=True))
        batch_op.alter_column('teacher_id',
               existing_type=sa.BIGINT(),
               nullable=True)
        batch_op.create_unique_constraint('uq_section_class_name', ['class_id', 'name'])
        batch_op.create_foreign_key('fk_sections_class_id', 'school_classes', ['class_id'], ['id'])

    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('roll_number', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('admission_number', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('guardian_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('guardian_phone', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))
        batch_op.create_unique_constraint('uq_students_admission_number', ['admission_number'])

    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('class_id', sa.BigInteger(), nullable=True))
        batch_op.alter_column('teacher_id',
               existing_type=sa.BIGINT(),
               nullable=True)
        batch_op.alter_column('course_id',
               existing_type=sa.BIGINT(),
               nullable=True)
        batch_op.create_unique_constraint('uq_subject_class_name', ['class_id', 'name'])
        batch_op.create_foreign_key('fk_subjects_class_id', 'school_classes', ['class_id'], ['id'])



def downgrade():
    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.drop_constraint('fk_subjects_class_id', type_='foreignkey')
        batch_op.drop_constraint('uq_subject_class_name', type_='unique')
        batch_op.alter_column('course_id',
               existing_type=sa.BIGINT(),
               nullable=False)
        batch_op.alter_column('teacher_id',
               existing_type=sa.BIGINT(),
               nullable=False)
        batch_op.drop_column('class_id')

    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.drop_constraint('uq_students_admission_number', type_='unique')
        batch_op.drop_column('date_of_birth')
        batch_op.drop_column('guardian_phone')
        batch_op.drop_column('guardian_name')
        batch_op.drop_column('admission_number')
        batch_op.drop_column('roll_number')

    with op.batch_alter_table('sections', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sections_class_id', type_='foreignkey')
        batch_op.drop_constraint('uq_section_class_name', type_='unique')
        batch_op.alter_column('teacher_id',
               existing_type=sa.BIGINT(),
               nullable=False)
        batch_op.drop_column('class_id')

    op.drop_table('teaching_assignments')
    op.drop_table('syllabus_chapters')
    op.drop_table('school_classes')
    op.drop_table('academic_sessions')
