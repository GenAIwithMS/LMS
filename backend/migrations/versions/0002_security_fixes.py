"""Security fixes: unique usernames and emails, chat history, pending deletes, logged-out tokens.

Fails if two users already share a username or email in the same table:
fix those accounts first (change the username or email of the extra one).

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def find_duplicates():
    """List usernames and emails used more than once in the same table."""
    connection = op.get_bind()
    problems = []
    for table in ['students', 'teachers', 'admin']:
        for column in ['username', 'email']:
            rows = connection.execute(sa.text(
                f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} HAVING COUNT(*) > 1"
            )).fetchall()
            for row in rows:
                problems.append(f"{table}.{column} '{row[0]}' is used {row[1]} times")
    return problems


def upgrade():
    # Check first, so nothing is changed when there are duplicates
    problems = find_duplicates()
    if problems:
        raise RuntimeError(
            "Cannot make usernames and emails unique. Fix these accounts first "
            "(change the username or email of the extra ones), then run the upgrade again:\n  - "
            + "\n  - ".join(problems)
        )

    # Usernames and emails must be unique
    with op.batch_alter_table('students') as batch_op:
        batch_op.create_unique_constraint('uq_students_username', ['username'])
        batch_op.create_unique_constraint('uq_students_email', ['email'])
    with op.batch_alter_table('teachers') as batch_op:
        batch_op.create_unique_constraint('uq_teachers_username', ['username'])
        batch_op.create_unique_constraint('uq_teachers_email', ['email'])
    with op.batch_alter_table('admin') as batch_op:
        batch_op.create_unique_constraint('uq_admin_username', ['username'])
        batch_op.create_unique_constraint('uq_admin_email', ['email'])

    # New tables
    op.create_table('chat_messages',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('user_role', sa.Enum('admin', 'teacher', 'student'), nullable=False),
    sa.Column('sender', sa.Enum('user', 'assistant'), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chat_pending_actions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('user_role', sa.Enum('admin', 'teacher', 'student'), nullable=False),
    sa.Column('tool_name', sa.String(length=100), nullable=False),
    sa.Column('tool_args', sa.Text(), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('status', sa.Enum('waiting', 'done', 'cancelled'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('revoked_tokens',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('jti', sa.String(length=64), nullable=False),
    sa.Column('revoked_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('jti')
    )


def downgrade():
    op.drop_table('revoked_tokens')
    op.drop_table('chat_pending_actions')
    op.drop_table('chat_messages')

    with op.batch_alter_table('admin') as batch_op:
        batch_op.drop_constraint('uq_admin_email', type_='unique')
        batch_op.drop_constraint('uq_admin_username', type_='unique')
    with op.batch_alter_table('teachers') as batch_op:
        batch_op.drop_constraint('uq_teachers_email', type_='unique')
        batch_op.drop_constraint('uq_teachers_username', type_='unique')
    with op.batch_alter_table('students') as batch_op:
        batch_op.drop_constraint('uq_students_email', type_='unique')
        batch_op.drop_constraint('uq_students_username', type_='unique')
