from flask import jsonify
from src.db import db
from src.models import TimetablePeriod, Section, Subject, TeachingAssignment, Teacher


# The weekly timetable: for each section, which subject is in each period, Monday to Saturday.
# The admin fills it in. The teacher of a period is whoever teaches that subject in
# that section, and a teacher can't be in two sections in the same period.

DAY_NAMES = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
PERIODS_PER_DAY = 8


def get_period_teacher(section_id, subject_id):
    """The teacher of this subject in this section, or None if the admin hasn't chosen one."""
    teaching = TeachingAssignment.query.filter_by(section_id=section_id, subject_id=subject_id).first()
    if teaching:
        return teaching.teacher
    return None


def find_teacher_clash(teacher_id, day, period, section_id):
    """Another section's period that this teacher already teaches at the same time, or None."""
    periods = TimetablePeriod.query.filter_by(day=day, period=period).all()
    for other in periods:
        if other.section_id == section_id:
            continue
        other_teacher = get_period_teacher(other.section_id, other.subject_id)
        if other_teacher and other_teacher.id == teacher_id:
            return other
    return None


def clash_message(teacher_name, clash):
    return (f"{teacher_name} already teaches {clash.subject.name} in {clash.section.full_name()} "
            f"in period {clash.period} on {DAY_NAMES[clash.day]}")


def slot_data(timetable_period):
    teacher = get_period_teacher(timetable_period.section_id, timetable_period.subject_id)
    return {
        "id": timetable_period.id,
        "section_id": timetable_period.section_id,
        "section_name": timetable_period.section.full_name(),
        "day": timetable_period.day,
        "day_name": DAY_NAMES[timetable_period.day],
        "period": timetable_period.period,
        "subject_id": timetable_period.subject_id,
        "subject_name": timetable_period.subject.name,
        "teacher_id": teacher.id if teacher else None,
        "teacher_name": teacher.name if teacher else None
    }


def week_layout():
    """The days and number of periods, so pages can draw the timetable grid."""
    day_list = []
    for day_number in DAY_NAMES:
        day_list.append({"day": day_number, "name": DAY_NAMES[day_number]})
    return day_list


def get_section_timetable(section_id):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    periods = TimetablePeriod.query.filter_by(section_id=section_id).order_by(TimetablePeriod.day, TimetablePeriod.period).all()
    slot_list = []
    for timetable_period in periods:
        slot_list.append(slot_data(timetable_period))

    return jsonify({
        "section_id": section.id,
        "section_name": section.full_name(),
        "days": week_layout(),
        "periods_per_day": PERIODS_PER_DAY,
        "slots": slot_list
    })


def set_timetable_slot(section_id, day, period, subject_id):
    """Put a subject in a period of the section's week. subject_id None empties the period."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    if day not in DAY_NAMES:
        return jsonify({"message": "Day must be 1 (Monday) to 6 (Saturday)", "status": "failed"}), 400
    if period < 1 or period > PERIODS_PER_DAY:
        return jsonify({"message": f"Period must be 1 to {PERIODS_PER_DAY}", "status": "failed"}), 400

    existing = TimetablePeriod.query.filter_by(section_id=section_id, day=day, period=period).first()

    if subject_id is None:
        if existing:
            db.session.delete(existing)
            db.session.commit()
        return jsonify({"message": f"Period {period} on {DAY_NAMES[day]} is now free", "status": "success"})

    subject = Subject.query.get(subject_id)
    if not subject or subject.class_id != section.class_id:
        return jsonify({"message": "This subject is not part of this section's class", "status": "failed"}), 400

    teacher = get_period_teacher(section_id, subject_id)
    if teacher:
        clash = find_teacher_clash(teacher.id, day, period, section_id)
        if clash:
            return jsonify({"message": clash_message(teacher.name, clash), "status": "failed"}), 409

    if existing:
        existing.subject_id = subject_id
    else:
        db.session.add(TimetablePeriod(section_id=section_id, day=day, period=period, subject_id=subject_id))
    db.session.commit()

    return jsonify({"message": f"{subject.name} set for period {period} on {DAY_NAMES[day]}", "status": "success"})


def check_new_subject_teacher(section_id, subject_id, teacher_id):
    """Before the admin changes who teaches a subject in a section: an error message if
    the new teacher is already busy in another section during one of its periods, otherwise None."""
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return None

    periods = TimetablePeriod.query.filter_by(section_id=section_id, subject_id=subject_id).all()
    for timetable_period in periods:
        clash = find_teacher_clash(teacher.id, timetable_period.day, timetable_period.period, section_id)
        if clash:
            return clash_message(teacher.name, clash)
    return None


def get_teacher_timetable(teacher_id):
    """A teacher's own week: every period, in any section, of a subject they teach there."""
    slot_list = []
    for teaching in TeachingAssignment.query.filter_by(teacher_id=teacher_id).all():
        periods = TimetablePeriod.query.filter_by(section_id=teaching.section_id, subject_id=teaching.subject_id).all()
        for timetable_period in periods:
            slot_list.append(slot_data(timetable_period))

    slot_list.sort(key=lambda slot: (slot["day"], slot["period"]))

    return jsonify({
        "days": week_layout(),
        "periods_per_day": PERIODS_PER_DAY,
        "slots": slot_list
    })
