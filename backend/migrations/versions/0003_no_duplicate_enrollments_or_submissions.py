"""One enrollment per student and course, one submission per student and assignment.

Fails with a list if the database already has duplicates: remove the extra
enrollments or submissions first, then run the upgrade again.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa


revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def find_duplicates():
    """List student/course and student/assignment pairs that appear more than once."""
    connection = op.get_bind()
    problems = []

    rows = connection.execute(sa.text(
        "SELECT student_id, course_id, COUNT(*) FROM enrollment "
        "GROUP BY student_id, course_id HAVING COUNT(*) > 1"
    )).fetchall()
    for row in rows:
        problems.append(f"student {row[0]} is enrolled in course {row[1]} {row[2]} times")

    rows = connection.execute(sa.text(
        "SELECT student_id, assignment_id, COUNT(*) FROM assignment_submission "
        "GROUP BY student_id, assignment_id HAVING COUNT(*) > 1"
    )).fetchall()
    for row in rows:
        problems.append(f"student {row[0]} has {row[2]} submissions for assignment {row[1]}")

    return problems


def upgrade():
    # Check first, so nothing is changed when there are duplicates
    problems = find_duplicates()
    if problems:
        raise RuntimeError(
            "Cannot add the one-enrollment / one-submission rules. Remove the extra rows first, "
            "then run the upgrade again:\n  - " + "\n  - ".join(problems)
        )

    with op.batch_alter_table('enrollment') as batch_op:
        batch_op.create_unique_constraint('uq_enrollment_student_course', ['student_id', 'course_id'])
    with op.batch_alter_table('assignment_submission') as batch_op:
        batch_op.create_unique_constraint('uq_submission_student_assignment', ['student_id', 'assignment_id'])


def downgrade():
    with op.batch_alter_table('assignment_submission') as batch_op:
        batch_op.drop_constraint('uq_submission_student_assignment', type_='unique')
    with op.batch_alter_table('enrollment') as batch_op:
        batch_op.drop_constraint('uq_enrollment_student_course', type_='unique')
