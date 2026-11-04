from src.db import db
from src.extention import bcrypt

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    section_id = db.Column(db.BigInteger, db.ForeignKey("sections.id") , nullable=False)
    # School record (all optional, so older accounts still work)
    roll_number = db.Column(db.String(20), nullable=True)
    admission_number = db.Column(db.String(50), nullable=True, unique=True)
    guardian_name = db.Column(db.String(255), nullable=True)
    guardian_phone = db.Column(db.String(30), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    # Read-only shortcut to a student's courses. Enrollments are created and changed
    # through the Enrollment model, which also owns the status, grade and date.
    courses = db.relationship('Course', secondary='enrollment', backref=db.backref('students', viewonly=True), lazy=True, viewonly=True)
    section = db.relationship('Section', backref='students', lazy=True)

    def set_password(self, password):
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string")
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        if not isinstance(password, str) or not password:
            return False
        return bcrypt.check_password_hash(self.password, password)