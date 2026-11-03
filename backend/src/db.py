from datetime import datetime
from zoneinfo import ZoneInfo
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def pakistan_time():
    """The current date and time in Pakistan.

    Models use it as default=pakistan_time (no brackets), so it runs each time a
    row is created. Writing default=datetime.now(...) runs it only once, when the
    server starts, and gives every row the same time.
    """
    return datetime.now(ZoneInfo("Asia/Karachi"))


def pakistan_time_naive():
    """pakistan_time() without the time zone part.

    The database saves times without a time zone, so use this when comparing
    with saved times in a query.
    """
    return pakistan_time().replace(tzinfo=None)
