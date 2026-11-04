from src.db import db, pakistan_time


class SchoolPeriod(db.Model):
    """One slot of the school day (the bell schedule), e.g. Period 1 08:00-08:40, or a break.

    Class periods are numbered 1, 2, 3...; a break has no number and can't hold a subject.
    The timetable (TimetablePeriod.period) uses these numbers.
    """
    __tablename__ = 'school_periods'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=True, unique=True)    # None for a break
    name = db.Column(db.String(50), nullable=False)               # "Period 1", "Lunch Break"
    start_time = db.Column(db.String(5), nullable=False)          # "08:00"
    end_time = db.Column(db.String(5), nullable=False)            # "08:40"
    is_break = db.Column(db.Boolean, nullable=False, default=False)


class SchoolSetting(db.Model):
    """A simple school-wide setting, like the school days ("1,2,3,4,5,6" = Monday to Saturday)."""
    __tablename__ = 'school_settings'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)


class TimetableVersion(db.Model):
    """One published timetable for the whole school. Teachers and students see the newest one.

    The admin edits a draft (TimetablePeriod); publishing copies the draft here, so later
    edits don't reach anyone until the admin publishes again.
    """
    __tablename__ = 'timetable_versions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    published_at = db.Column(db.DateTime, default=pakistan_time, nullable=False)
    published_by = db.Column(db.String(255), nullable=True)
    days = db.Column(db.String(20), nullable=False)          # "1,2,3,4,5,6"
    periods_json = db.Column(db.Text, nullable=False)        # the bell schedule when published
    draft_signature = db.Column(db.String(64), nullable=False)   # to notice changes made after publishing


class PublishedPeriod(db.Model):
    """One period of a published timetable, with the subject and teacher as they were when published."""
    __tablename__ = 'published_periods'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    version_id = db.Column(db.BigInteger, db.ForeignKey('timetable_versions.id'), nullable=False)
    # A copy, not a link: deleting a section later doesn't change what was published
    section_id = db.Column(db.BigInteger, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.BigInteger, nullable=True)
    subject_name = db.Column(db.String(255), nullable=False)
    teacher_id = db.Column(db.BigInteger, nullable=True)
    teacher_name = db.Column(db.String(255), nullable=True)
    section_name = db.Column(db.String(255), nullable=False)

    version = db.relationship('TimetableVersion', backref='periods', lazy=True)
