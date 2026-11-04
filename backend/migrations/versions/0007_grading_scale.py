"""The school's grading scale, editable by the admin. Starts with the scale used by
most Pakistani schools and boards: A+ 80, A 70, B 60, C 50, D 40, E 33, F below 33.

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-04 20:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('grade_bands',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('grade', sa.String(length=5), nullable=False),
    sa.Column('min_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('grade', name='uq_grade_bands_grade'),
    sa.UniqueConstraint('min_percentage', name='uq_grade_bands_min_percentage')
    )

    # The default scale
    grade_bands = sa.table('grade_bands', sa.column('id', sa.BigInteger), sa.column('grade', sa.String), sa.column('min_percentage', sa.Numeric))
    rows = []
    defaults = [("A+", 80), ("A", 70), ("B", 60), ("C", 50), ("D", 40), ("E", 33), ("F", 0)]
    for index, (grade, min_percentage) in enumerate(defaults):
        rows.append({"id": index + 1, "grade": grade, "min_percentage": min_percentage})
    op.bulk_insert(grade_bands, rows)


def downgrade():
    op.drop_table('grade_bands')
