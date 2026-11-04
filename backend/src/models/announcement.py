from src.db import db, pakistan_time


class Announcement(db.Model):
    """A notice posted by a teacher (for one of their sections) or by the admin.

    Who it is for:
    - target_audience: "all" (teachers and students), "teachers" or "students"
    - where: the whole school (no class, no section), one class (class_id: every section
      of it) or one section (section_id)
    """
    __tablename__ = 'announcements'
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # The author: a teacher, or the admin (exactly one of the two is set)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=True)
    admin_id = db.Column(db.BigInteger, db.ForeignKey('admin.id'), nullable=True)
    target_audience = db.Column(db.String(50), default='all')
    class_id = db.Column(db.BigInteger, db.ForeignKey('school_classes.id'), nullable=True)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=True)
    # Posted by the section's class incharge as a class announcement (shown in its own colour)
    from_incharge = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=pakistan_time)

    section = db.relationship("Section", backref="announcements",lazy=True)
    teacher = db.relationship("Teacher", backref="announcements",lazy=True)
    admin = db.relationship("Admin", lazy=True)
    school_class = db.relationship("SchoolClass", lazy=True)
