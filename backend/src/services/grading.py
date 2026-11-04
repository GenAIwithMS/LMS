from decimal import Decimal
from flask import jsonify, g, has_request_context
from src.db import db
from src.models import GradeBand


# The school's grading scale. It starts with the scale used by most Pakistani
# schools and boards; the admin can change it (or reset it) from the admin panel.

DEFAULT_SCALE = [
    ("A+", 80),
    ("A", 70),
    ("B", 60),
    ("C", 50),
    ("D", 40),
    ("E", 33),
    ("F", 0),
]


def make_sure_scale_exists():
    """Add the default scale if the school has none yet (the migration also does this)."""
    if GradeBand.query.count() == 0:
        for grade, min_percentage in DEFAULT_SCALE:
            db.session.add(GradeBand(grade=grade, min_percentage=min_percentage))
        db.session.commit()


def load_scale():
    """The scale as a list of (grade, min_percentage), highest first.

    Read once per request: a report card asks for many grades.
    """
    if has_request_context() and "grade_scale" in g:
        return g.grade_scale

    make_sure_scale_exists()
    scale = []
    for band in GradeBand.query.order_by(GradeBand.min_percentage.desc()).all():
        scale.append((band.grade, float(band.min_percentage)))

    if has_request_context():
        g.grade_scale = scale
    return scale


def grade_for(percentage):
    """The grade for a percentage, or None when there is no percentage."""
    if percentage is None:
        return None
    scale = load_scale()
    for grade, min_percentage in scale:
        if percentage >= min_percentage:
            return grade
    # Can't normally happen: the lowest band starts at 0
    return scale[-1][0]


def scale_data():
    """The scale for pages and report cards: highest grade first."""
    band_list = []
    for grade, min_percentage in load_scale():
        band_list.append({"grade": grade, "min_percentage": min_percentage})
    return band_list


def get_grade_scale():
    return jsonify(scale_data())


def check_bands(bands):
    """An error message if the new scale isn't usable, otherwise None.
    bands: [{"grade": "A+", "min_percentage": 80}, ...]"""
    if len(bands) < 2:
        return "The scale needs at least two grades"

    grades = []
    percentages = []
    for band in bands:
        grade = band["grade"].strip()
        if grade == "":
            return "Every grade needs a name"
        if grade.upper() in grades:
            return f"Grade {grade} is in the list twice"
        if band["min_percentage"] in percentages:
            return f"Two grades start at {band['min_percentage']}%"
        grades.append(grade.upper())
        percentages.append(band["min_percentage"])

    # Every percentage must get a grade, so the lowest grade starts at 0
    if Decimal("0") not in percentages:
        return "The lowest grade must start at 0% (for example F from 0%)"
    return None


def save_grade_scale(bands):
    """Replace the whole scale with these grades."""
    problem = check_bands(bands)
    if problem:
        return jsonify({"message": problem, "status": "failed"}), 400

    GradeBand.query.delete()
    for band in bands:
        db.session.add(GradeBand(grade=band["grade"].strip(), min_percentage=band["min_percentage"]))
    db.session.commit()

    if has_request_context() and "grade_scale" in g:
        g.pop("grade_scale")
    return jsonify({"message": "Grading scale saved", "status": "success", "scale": scale_data()})


def reset_grade_scale():
    """Go back to the default scale."""
    GradeBand.query.delete()
    db.session.commit()
    if has_request_context() and "grade_scale" in g:
        g.pop("grade_scale")
    make_sure_scale_exists()
    return jsonify({"message": "Grading scale reset to the default", "status": "success", "scale": scale_data()})
