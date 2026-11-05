"""Shared helper for the check scripts (not a check itself).

Older check scripts set up data the old way: a subject has one teacher, and a
teacher leads sections. In the school system, who teaches a subject is set per
section (TeachingAssignment). This turns the old setup into the new one: each
subject's teacher teaches it in the sections they lead.
"""
from src.db import db
from src.models import Subject, Section, TeachingAssignment


def give_teachers_their_subjects():
    for subject in Subject.query.all():
        if not subject.teacher_id:
            continue
        for section in Section.query.filter_by(teacher_id=subject.teacher_id).all():
            existing = TeachingAssignment.query.filter_by(section_id=section.id, subject_id=subject.id).first()
            if not existing:
                db.session.add(TeachingAssignment(section_id=section.id, subject_id=subject.id, teacher_id=subject.teacher_id))
    db.session.commit()


def make_every_day_a_school_day():
    """The check scripts mark attendance for "today". Attendance is only allowed on school
    days, so the test database counts every day (Monday to Sunday) as a school day; then
    the checks pass whatever day they are run on."""
    from src.models import SchoolSetting
    from src.services.timetable import make_sure_layout_exists
    make_sure_layout_exists()
    setting = SchoolSetting.query.filter_by(key="school_days").first()
    setting.value = "1,2,3,4,5,6,7"
    db.session.commit()
