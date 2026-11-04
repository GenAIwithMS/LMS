from src.db import db

class Section(db.Model):
    """A section of a class, like 5-A. teacher_id is the section's class incharge."""
    __tablename__ = 'sections'
    __table_args__ = (db.UniqueConstraint('class_id', 'name', name='uq_section_class_name'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    class_id = db.Column(db.BigInteger, db.ForeignKey("school_classes.id"), nullable=True)
    # The class incharge (class teacher). Empty until the admin picks one.
    teacher_id = db.Column(db.BigInteger, db.ForeignKey("teachers.id"), nullable=True)

    teacher = db.relationship('Teacher', backref='sections', lazy=True)
    school_class = db.relationship('SchoolClass', backref='sections', lazy=True)

    def full_name(self):
        """Like "Class 5 - A". Sections from before the school system have no class."""
        if self.school_class:
            return f"{self.school_class.name} - {self.name}"
        return self.name
