from src.models import Admin, Teacher, Student


def is_email_taken(email, current_user=None):
    """Check if an admin, teacher or student already uses this email.

    current_user is the record being updated. Its own email does not count as taken.
    """
    for model in [Admin, Teacher, Student]:
        user = model.query.filter_by(email=email).first()
        if user and user is not current_user:
            return True
    return False


def is_username_taken(username, current_user=None):
    """Check if an admin, teacher or student already uses this username.

    current_user is the record being updated. Its own username does not count as taken.
    """
    for model in [Admin, Teacher, Student]:
        user = model.query.filter_by(username=username).first()
        if user and user is not current_user:
            return True
    return False
