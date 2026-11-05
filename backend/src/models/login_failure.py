from src.db import db, pakistan_time_naive


class LoginFailure(db.Model):
    """One wrong password for an account. Kept in the database (not in the server's memory)
    so every server process sees the same count, and the account is protected even when
    the guesses come from many different addresses. Cleared after a successful login."""
    __tablename__ = 'login_failures'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, index=True)   # always stored in lower case
    ip_address = db.Column(db.String(64), nullable=True)
    failed_at = db.Column(db.DateTime, nullable=False, default=pakistan_time_naive, index=True)
