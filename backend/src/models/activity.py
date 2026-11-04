from src.db import db, pakistan_time


class ActivityLog(db.Model):
    """One thing someone did in the LMS: logged in, marked attendance, entered marks...

    Filled in automatically after every change (see services/activity_log.py).
    Request bodies are never stored, so no passwords or marks end up here.

    action is one of: login, login_failed, logout, create, update, delete.
    """
    __tablename__ = 'activity_logs'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=pakistan_time, nullable=False, index=True)
    user_role = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.BigInteger, nullable=True)
    user_name = db.Column(db.String(255), nullable=True)
    action = db.Column(db.String(20), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    status_code = db.Column(db.Integer, nullable=False)
    section_id = db.Column(db.BigInteger, nullable=True)
    class_id = db.Column(db.BigInteger, nullable=True)

    __table_args__ = (db.Index('ix_activity_logs_user', 'user_role', 'user_id'),)
