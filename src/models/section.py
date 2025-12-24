from src.db import db

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey("teachers.id"), nullable=False)

    teacher = db.relationship('Teacher', backref='teacher_sections', lazy=True)