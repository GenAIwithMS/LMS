from src.db import db
from src.models import Subject, TeacherSubject


# The subjects each teacher can teach, by name ("Urdu"), set before giving them any class.
# Used by the school structure and by the timetable.


def same_name(first, second):
    return first.strip().lower() == second.strip().lower()


def name_in_list(name, names):
    """True if the name is in the list, ignoring capitals and spaces at the ends."""
    for other in names:
        if same_name(other, name):
            return True
    return False


def neat_subject_name(name):
    """Use the spelling of an existing subject ("urdu" becomes "Urdu"), or the name as typed."""
    name = name.strip()
    for subject in Subject.query.all():
        if same_name(subject.name, name):
            return subject.name
    for skill in TeacherSubject.query.all():
        if same_name(skill.subject_name, name):
            return skill.subject_name
    # A new subject: start it with a capital letter ("islamiyat" becomes "Islamiyat"; "ICT" stays "ICT")
    if name != "":
        name = name[0].upper() + name[1:]
    return name


def teacher_skill_names(teacher_id):
    names = []
    for skill in TeacherSubject.query.filter_by(teacher_id=teacher_id).order_by(TeacherSubject.subject_name).all():
        names.append(skill.subject_name)
    return names


def add_skill_if_missing(teacher_id, subject_name):
    """Record that the teacher teaches this subject (doesn't commit)."""
    if name_in_list(subject_name, teacher_skill_names(teacher_id)):
        return
    db.session.add(TeacherSubject(teacher_id=teacher_id, subject_name=neat_subject_name(subject_name)))
