from src.db import db


class GradeBand(db.Model):
    """One grade of the school's grading scale, e.g. "A+" from 80%.

    A student gets the grade with the highest min_percentage they reach.
    The lowest band always starts at 0, so every percentage has a grade.
    """
    __tablename__ = 'grade_bands'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    grade = db.Column(db.String(5), nullable=False, unique=True)
    min_percentage = db.Column(db.Numeric(5, 2), nullable=False, unique=True)
