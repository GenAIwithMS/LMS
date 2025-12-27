from src.db import db
from src.extention import bcrypt

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    section_id = db.Column(db.BigInteger, db.ForeignKey("sections.id") , nullable=False)

    courses = db.relationship('Course', secondary='enrollment', backref='students', lazy=True)
    section = db.relationship('Section', backref='students', lazy=True)

    def set_password(self, password):
        if not isinstance(password, str) or not password:
            raise ValueError("Password must be a non-empty string")
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        if not isinstance(password, str) or not password:
            return False
        return bcrypt.check_password_hash(self.password, password)