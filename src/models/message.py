from src.db import db

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.BigInteger, nullable=False)
    sender_type = db.Column(db.Enum('admin', 'teacher', 'student'), nullable=False)
    receiver_id = db.Column(db.BigInteger, nullable=False)
    receiver_type = db.Column(db.Enum('admin', 'teacher', 'student'), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=db.func.current_timestamp())