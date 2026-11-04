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
