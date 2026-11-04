"""The subjects each teacher can teach (like "Urdu"), set before giving them any class.

Filled in from what teachers already teach, so nothing has to be entered again.

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-05 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('teacher_subjects',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('teacher_id', sa.BigInteger(), nullable=False),
    sa.Column('subject_name', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name='fk_teacher_subjects_teacher_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('teacher_id', 'subject_name', name='uq_teacher_subject_name')
    )

    # Every subject a teacher already teaches in a section. The IDs are given here because
    # SQLite (used by the tests) doesn't number BIGINT keys by itself.
    connection = op.get_bind()
    rows = connection.execute(sa.text(
        "SELECT DISTINCT teaching_assignments.teacher_id, subjects.name "
        "FROM teaching_assignments JOIN subjects ON subjects.id = teaching_assignments.subject_id"
    )).fetchall()

    teacher_subjects = sa.table('teacher_subjects', sa.column('id', sa.BigInteger), sa.column('teacher_id', sa.BigInteger),
                                sa.column('subject_name', sa.String))
    new_rows = []
    seen = []
    for teacher_id, subject_name in rows:
        key = (teacher_id, subject_name.strip().lower())
        if key in seen:
            continue
        seen.append(key)
        new_rows.append({"id": len(new_rows) + 1, "teacher_id": teacher_id, "subject_name": subject_name})
    if len(new_rows) > 0:
        op.bulk_insert(teacher_subjects, new_rows)


def downgrade():
    op.drop_table('teacher_subjects')
