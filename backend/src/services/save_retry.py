import random
import time
from flask import jsonify
from sqlalchemy.exc import OperationalError, IntegrityError
from src.db import db


# When two people (or one double-click) save the same record at the same moment, the
# database lets one save through and refuses the other:
#   1020 "Record has changed since last read" (MariaDB)
#   1213 deadlock, 1205 lock wait timeout
#   1062 duplicate entry (both tried to add the same new row, e.g. the same day's attendance)
# Trying again a moment later almost always works, because by then the other save is done.
CONFLICT_CODES = [1020, 1213, 1205]
DUPLICATE_CODE = 1062

CONFLICT_MESSAGE = "Someone saved this at the same moment. Please try again."


def error_code(error):
    """The database's error number inside a SQLAlchemy error, or None."""
    original = getattr(error, "orig", None)
    if original is None:
        return None
    arguments = getattr(original, "args", None)
    if not arguments:
        return None
    return arguments[0]


def is_save_conflict(error):
    """True if the error means "someone else saved this at the same moment"."""
    if isinstance(error, OperationalError) and error_code(error) in CONFLICT_CODES:
        return True
    if isinstance(error, IntegrityError) and error_code(error) == DUPLICATE_CODE:
        return True
    return False


def conflict_answer():
    return jsonify({"message": CONFLICT_MESSAGE, "status": "failed"}), 409


def wait_for_section(section_id):
    """Make saves of one section's register or diary take turns: the second waits until the
    first is finished, instead of clashing with it. (MySQL locks the section's row until this
    save is committed. SQLite, used by the tests, has no row locks and needs none.)"""
    if db.engine.dialect.name != "mysql":
        return
    # Start a fresh transaction, so this save reads what the previous one saved
    db.session.commit()
    db.session.execute(
        db.text("SELECT id FROM sections WHERE id = :section_id FOR UPDATE"),
        {"section_id": section_id}
    )


def save_with_retry(save, attempts=3):
    """Run save() (which saves and returns the answer). If it clashes with another save
    of the same record, undo and try again, up to `attempts` times; then answer 409."""
    for attempt in range(1, attempts + 1):
        try:
            return save()
        except (OperationalError, IntegrityError) as error:
            if not is_save_conflict(error):
                raise
            db.session.rollback()
            if attempt == attempts:
                break
            # Wait a little (longer each time, and not exactly in step with the other save)
            time.sleep(random.uniform(0.05, 0.15) * attempt)
    return conflict_answer()
