"""Each section has its own syllabus, written by its subject teacher, and chapters have
daily topics. Assignments, class tests and diary entries can point to the topic they were
made from.

The existing chapters belonged to a subject of a class (shared by all its sections). Each is
copied into every section of that class, and each section's progress and class tests are
moved to its own copy, so nothing is lost.

Revision ID: 0014
Revises: 0013
Create Date: 2026-11-08 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    # Chapters get a section
    op.add_column('syllabus_chapters', sa.Column('section_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_syllabus_chapters_section_id', 'syllabus_chapters', 'sections', ['section_id'], ['id'])
    # The new rule starts with subject_id, so the subject's foreign key keeps an index
    op.create_unique_constraint('uq_chapter_subject_section_number', 'syllabus_chapters', ['subject_id', 'section_id', 'number'])
    op.drop_constraint('uq_chapter_subject_number', 'syllabus_chapters', type_='unique')

    # Copy each class-level chapter into every section of its class
    chapters = connection.execute(sa.text(
        "SELECT c.id, c.subject_id, c.number, c.title, c.description, s.class_id "
        "FROM syllabus_chapters c JOIN subjects s ON s.id = c.subject_id WHERE c.section_id IS NULL"
    )).fetchall()
    for chapter_id, subject_id, number, title, description, class_id in chapters:
        if class_id is None:
            continue
        sections = connection.execute(sa.text("SELECT id FROM sections WHERE class_id = :class_id ORDER BY id"),
                                      {"class_id": class_id}).fetchall()
        for index, (section_id,) in enumerate(sections):
            if index == 0:
                # The first section keeps the original chapter
                connection.execute(sa.text("UPDATE syllabus_chapters SET section_id = :section_id WHERE id = :id"),
                                   {"section_id": section_id, "id": chapter_id})
                continue
            result = connection.execute(sa.text(
                "INSERT INTO syllabus_chapters (subject_id, section_id, number, title, description) "
                "VALUES (:subject_id, :section_id, :number, :title, :description)"),
                {"subject_id": subject_id, "section_id": section_id, "number": number, "title": title, "description": description})
            copy_id = result.lastrowid
            # This section's progress and tests now point to its own copy
            connection.execute(sa.text("UPDATE chapter_progress SET chapter_id = :copy_id WHERE chapter_id = :id AND section_id = :section_id"),
                               {"copy_id": copy_id, "id": chapter_id, "section_id": section_id})
            connection.execute(sa.text("UPDATE class_tests SET chapter_id = :copy_id WHERE chapter_id = :id AND section_id = :section_id"),
                               {"copy_id": copy_id, "id": chapter_id, "section_id": section_id})

    # Daily topics
    op.create_table(
        'syllabus_topics',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('chapter_id', sa.BigInteger(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('planned_date', sa.Date(), nullable=True),
        sa.Column('is_done', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('done_on', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['chapter_id'], ['syllabus_chapters.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chapter_id', 'number', name='uq_topic_chapter_number'),
    )

    # What was made from a topic
    for table in ['assignments', 'class_tests', 'diary_entries']:
        op.add_column(table, sa.Column('topic_id', sa.BigInteger(), nullable=True))
        op.create_foreign_key(f'fk_{table}_topic_id', table, 'syllabus_topics', ['topic_id'], ['id'])


def downgrade():
    for table in ['assignments', 'class_tests', 'diary_entries']:
        op.drop_constraint(f'fk_{table}_topic_id', table, type_='foreignkey')
        op.drop_column(table, 'topic_id')
    op.drop_table('syllabus_topics')
    # Back to one chapter list per subject: keep only the first section's chapters
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE class_tests SET chapter_id = NULL WHERE chapter_id IN "
        "(SELECT id FROM (SELECT c.id FROM syllabus_chapters c WHERE c.id NOT IN "
        "(SELECT MIN(id) FROM syllabus_chapters GROUP BY subject_id, number)) x)"))
    connection.execute(sa.text(
        "DELETE FROM chapter_progress WHERE chapter_id IN "
        "(SELECT id FROM (SELECT c.id FROM syllabus_chapters c WHERE c.id NOT IN "
        "(SELECT MIN(id) FROM syllabus_chapters GROUP BY subject_id, number)) x)"))
    connection.execute(sa.text(
        "DELETE FROM syllabus_chapters WHERE id NOT IN "
        "(SELECT id FROM (SELECT MIN(id) AS id FROM syllabus_chapters GROUP BY subject_id, number) x)"))
    op.create_unique_constraint('uq_chapter_subject_number', 'syllabus_chapters', ['subject_id', 'number'])
    op.drop_constraint('uq_chapter_subject_section_number', 'syllabus_chapters', type_='unique')
    op.drop_constraint('fk_syllabus_chapters_section_id', 'syllabus_chapters', type_='foreignkey')
    op.drop_column('syllabus_chapters', 'section_id')
