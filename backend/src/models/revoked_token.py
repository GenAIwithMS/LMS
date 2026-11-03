from src.db import db, pakistan_time


class RevokedToken(db.Model):
    """A login token that was logged out. It can't be used again, even before it expires.

    revoked_at is when the block starts. A normal logout blocks straight away.
    When a tab is closed the block starts a few seconds later, so that a page
    refresh (which also "closes" the page for a moment) can cancel it.
    """
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(64), nullable=False, unique=True)   # the token's unique id
    revoked_at = db.Column(db.DateTime, default=pakistan_time)
