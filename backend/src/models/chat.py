from src.db import db, pakistan_time


class ChatMessage(db.Model):
    """One message in a user's conversation with the LMS assistant.

    The conversation is kept on the server, so the browser can't change what
    the assistant "said" earlier.
    """
    __tablename__ = 'chat_messages'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    user_role = db.Column(db.Enum('admin', 'teacher', 'student'), nullable=False)
    sender = db.Column(db.Enum('user', 'assistant'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=pakistan_time)


class PendingAction(db.Model):
    """A delete the assistant wants to do, waiting for the user to click Confirm or Cancel.

    The assistant can't confirm it by itself: only the user's click does.
    """
    __tablename__ = 'chat_pending_actions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    user_role = db.Column(db.Enum('admin', 'teacher', 'student'), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    tool_args = db.Column(db.Text, nullable=False)   # the tool's arguments, as JSON
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Enum('waiting', 'done', 'cancelled'), nullable=False, default='waiting')
    created_at = db.Column(db.DateTime, default=pakistan_time)
