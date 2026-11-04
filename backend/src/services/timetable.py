import hashlib
import json
import re
from flask import jsonify
from src.db import db, pakistan_time
from src.models import (TimetablePeriod, Section, Subject, TeachingAssignment, Teacher, Student, SchoolPeriod,
                        SchoolSetting, TimetableVersion, PublishedPeriod)


# The school timetable.
#
# - The bell schedule (SchoolPeriod): the times of each period and break, set by the admin.
# - The school days: for example Monday to Saturday.
# - The draft: for each section, which subject is in each period. The teacher of a period is
#   whoever teaches that subject in that section, and a teacher can't be in two sections at once.
# - Publishing copies the draft for the whole school. Teachers and students only ever see
#   the published timetable, so the admin can work on changes without anyone seeing half of them.

DAY_NAMES = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
DEFAULT_DAYS = [1, 2, 3, 4, 5, 6]
MAX_CLASS_PERIODS = 12

# 8 periods of 40 minutes from 08:00, with a 20 minute break after period 4
DEFAULT_PERIODS = [
    ("Period 1", "08:00", "08:40", False),
    ("Period 2", "08:40", "09:20", False),
    ("Period 3", "09:20", "10:00", False),
    ("Period 4", "10:00", "10:40", False),
    ("Break", "10:40", "11:00", True),
    ("Period 5", "11:00", "11:40", False),
    ("Period 6", "11:40", "12:20", False),
    ("Period 7", "12:20", "13:00", False),
    ("Period 8", "13:00", "13:40", False),
]

TIME_PATTERN = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")


# ---------------- Bell schedule and school days

def days_text(days):
    """The days as saved, like "1,2,3,4,5,6"."""
    parts = []
    for day in days:
        parts.append(str(day))
    return ",".join(parts)


def make_sure_layout_exists():
    """Add the default bell schedule and school days if the school has none yet (the migration also does this)."""
    changed = False
    if SchoolPeriod.query.count() == 0:
        number = 0
        for name, start_time, end_time, is_break in DEFAULT_PERIODS:
            period_number = None
            if not is_break:
                number = number + 1
                period_number = number
            db.session.add(SchoolPeriod(number=period_number, name=name, start_time=start_time, end_time=end_time, is_break=is_break))
        changed = True
    if not SchoolSetting.query.filter_by(key="school_days").first():
        db.session.add(SchoolSetting(key="school_days", value=days_text(DEFAULT_DAYS)))
        changed = True
    if changed:
        db.session.commit()


def get_school_days():
    make_sure_layout_exists()
    setting = SchoolSetting.query.filter_by(key="school_days").first()
    days = []
    for part in setting.value.split(","):
        if part.strip() != "":
            days.append(int(part))
    return days


def get_period_rows():
    """The bell schedule in time order, as dicts."""
    make_sure_layout_exists()
    rows = []
    for school_period in SchoolPeriod.query.order_by(SchoolPeriod.start_time).all():
        rows.append({
            "number": school_period.number,
            "name": school_period.name,
            "start_time": school_period.start_time,
            "end_time": school_period.end_time,
            "is_break": school_period.is_break
        })
    return rows


def day_list(days):
    result = []
    for day in days:
        result.append({"day": day, "name": DAY_NAMES[day]})
    return result


def class_period_count(period_rows):
    count = 0
    for row in period_rows:
        if not row["is_break"]:
            count = count + 1
    return count


def layout_data():
    """The school days and the bell schedule, so pages can draw the timetable grid."""
    period_rows = get_period_rows()
    return {
        "days": day_list(get_school_days()),
        "periods": period_rows,
        "periods_per_day": class_period_count(period_rows)
    }


def get_timetable_settings():
    return jsonify(layout_data())


def save_timetable_settings(days, periods):
    """Replace the school days and the bell schedule.

    periods: [{"name", "start_time", "end_time", "is_break"}] in any order. Class periods are
    numbered again 1, 2, 3... by time. Draft periods on days or period numbers that no longer
    exist are removed (and counted in the answer).
    """
    # The days
    if len(days) == 0:
        return jsonify({"message": "Choose at least one school day", "status": "failed"}), 400
    clean_days = []
    for day in days:
        if day not in DAY_NAMES:
            return jsonify({"message": "Days must be 1 (Monday) to 7 (Sunday)", "status": "failed"}), 400
        if day not in clean_days:
            clean_days.append(day)
    clean_days.sort()

    # The periods: valid times, the end after the start, no two overlapping
    if len(periods) == 0:
        return jsonify({"message": "Add at least one period", "status": "failed"}), 400
    for row in periods:
        if not TIME_PATTERN.match(row["start_time"]) or not TIME_PATTERN.match(row["end_time"]):
            return jsonify({"message": "Times must look like 08:00 (24-hour clock)", "status": "failed"}), 400
        if row["end_time"] <= row["start_time"]:
            return jsonify({"message": f"{row['name']} must end after it starts", "status": "failed"}), 400
    ordered = sorted(periods, key=lambda row: row["start_time"])
    for index in range(1, len(ordered)):
        if ordered[index]["start_time"] < ordered[index - 1]["end_time"]:
            return jsonify({"message": f"{ordered[index - 1]['name']} and {ordered[index]['name']} overlap", "status": "failed"}), 400

    class_count = 0
    for row in ordered:
        if not row["is_break"]:
            class_count = class_count + 1
    if class_count == 0:
        return jsonify({"message": "The day needs at least one class period (not only breaks)", "status": "failed"}), 400
    if class_count > MAX_CLASS_PERIODS:
        return jsonify({"message": f"At most {MAX_CLASS_PERIODS} class periods a day", "status": "failed"}), 400

    # Save: the days, then the bell schedule (class periods numbered by time)
    setting = SchoolSetting.query.filter_by(key="school_days").first()
    if not setting:
        setting = SchoolSetting(key="school_days", value="")
        db.session.add(setting)
    setting.value = days_text(clean_days)

    SchoolPeriod.query.delete()
    number = 0
    for row in ordered:
        period_number = None
        if not row["is_break"]:
            number = number + 1
            period_number = number
        db.session.add(SchoolPeriod(number=period_number, name=row["name"].strip(), start_time=row["start_time"],
                                    end_time=row["end_time"], is_break=row["is_break"]))

    # Draft periods that no longer fit the week
    removed = 0
    for timetable_period in TimetablePeriod.query.all():
        if timetable_period.day not in clean_days or timetable_period.period > class_count:
            db.session.delete(timetable_period)
            removed = removed + 1
    db.session.commit()

    message = "Timetable settings saved"
    if removed > 0:
        message = message + f". {removed} period(s) on removed days or periods were taken out of the draft"
    return jsonify({"message": message, "status": "success", "removed": removed, "settings": layout_data()})


# ---------------- The draft (what the admin edits)

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


def section_subjects(section):
    """The section's subjects with their teachers, for the period choices."""
    subject_list = []
    if section.class_id:
        for subject in Subject.query.filter_by(class_id=section.class_id).order_by(Subject.name).all():
            teacher = get_period_teacher(section.id, subject.id)
            subject_list.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "teacher_id": teacher.id if teacher else None,
                "teacher_name": teacher.name if teacher else None
            })
    return subject_list


def get_section_timetable(section_id):
    """A section's draft timetable."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    periods = TimetablePeriod.query.filter_by(section_id=section_id).order_by(TimetablePeriod.day, TimetablePeriod.period).all()
    slot_list = []
    for timetable_period in periods:
        slot_list.append(slot_data(timetable_period))

    data = layout_data()
    data["section_id"] = section.id
    data["section_name"] = section.full_name()
    data["slots"] = slot_list
    return jsonify(data)


def set_timetable_slot(section_id, day, period, subject_id):
    """Put a subject in a period of the section's week. subject_id None empties the period."""
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404

    if day not in get_school_days():
        return jsonify({"message": "That day is not a school day", "status": "failed"}), 400
    period_count = class_period_count(get_period_rows())
    if period < 1 or period > period_count:
        return jsonify({"message": f"Period must be 1 to {period_count}", "status": "failed"}), 400

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


def clear_section_timetable(section_id):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"message": "Section not found", "status": "failed"}), 404
    TimetablePeriod.query.filter_by(section_id=section_id).delete()
    db.session.commit()
    return jsonify({"message": f"The timetable of {section.full_name()} is now empty", "status": "success"})


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


def get_school_draft():
    """Every section's draft, with its subjects and teachers, each teacher's periods per week,
    and whether the draft has changed since it was last published."""
    sections = Section.query.filter(Section.class_id.isnot(None)).all()
    sections.sort(key=lambda section: (section.school_class.level, section.name))

    section_list = []
    teacher_load = {}
    for section in sections:
        slot_list = []
        for timetable_period in TimetablePeriod.query.filter_by(section_id=section.id).all():
            slot = slot_data(timetable_period)
            slot_list.append(slot)
            if slot["teacher_id"]:
                if slot["teacher_id"] not in teacher_load:
                    teacher_load[slot["teacher_id"]] = {"teacher_id": slot["teacher_id"], "teacher_name": slot["teacher_name"], "periods": 0}
                teacher_load[slot["teacher_id"]]["periods"] = teacher_load[slot["teacher_id"]]["periods"] + 1

        section_list.append({
            "section_id": section.id,
            "section_name": section.full_name(),
            "class_id": section.class_id,
            "class_name": section.school_class.name,
            "incharge_name": section.teacher.name if section.teacher else None,
            "student_count": Student.query.filter_by(section_id=section.id).count(),
            "subjects": section_subjects(section),
            "slots": slot_list
        })

    load_list = []
    for teacher_id in teacher_load:
        load_list.append(teacher_load[teacher_id])
    load_list.sort(key=lambda item: item["teacher_name"])

    data = layout_data()
    data["sections"] = section_list
    data["teacher_load"] = load_list
    data["status"] = publish_status()
    return jsonify(data)


# ---------------- Publishing

def draft_signature():
    """A short fingerprint of the draft, the days and the bell schedule. It changes when any of them change."""
    rows = []
    for timetable_period in TimetablePeriod.query.all():
        teacher = get_period_teacher(timetable_period.section_id, timetable_period.subject_id)
        teacher_id = None
        if teacher:
            teacher_id = teacher.id
        rows.append([timetable_period.section_id, timetable_period.day, timetable_period.period, timetable_period.subject_id, teacher_id])
    rows.sort()
    text = json.dumps({"rows": rows, "days": get_school_days(), "periods": get_period_rows()}, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def latest_version():
    return TimetableVersion.query.order_by(TimetableVersion.published_at.desc(), TimetableVersion.id.desc()).first()


def publish_status():
    version = latest_version()
    if not version:
        return {"is_published": False, "published_at": None, "published_by": None, "has_unpublished_changes": True}
    return {
        "is_published": True,
        "published_at": version.published_at.strftime("%Y-%m-%d %H:%M"),
        "published_by": version.published_by,
        "has_unpublished_changes": version.draft_signature != draft_signature()
    }


def check_draft_problems():
    """(errors that stop publishing, warnings to show)."""
    errors = []
    warnings = []

    # A teacher in two sections at the same time (possible if teachers changed after periods were set)
    seen = {}
    for timetable_period in TimetablePeriod.query.all():
        teacher = get_period_teacher(timetable_period.section_id, timetable_period.subject_id)
        if not teacher:
            continue
        key = (teacher.id, timetable_period.day, timetable_period.period)
        if key in seen:
            other = seen[key]
            errors.append(f"{teacher.name} is in both {other.section.full_name()} and {timetable_period.section.full_name()} "
                          f"in period {timetable_period.period} on {DAY_NAMES[timetable_period.day]}")
        else:
            seen[key] = timetable_period

    # Periods whose subject has no teacher yet
    no_teacher = []
    for timetable_period in TimetablePeriod.query.all():
        if not get_period_teacher(timetable_period.section_id, timetable_period.subject_id):
            text = f"{timetable_period.subject.name} in {timetable_period.section.full_name()}"
            if text not in no_teacher:
                no_teacher.append(text)
    for text in no_teacher:
        warnings.append(f"{text} has no teacher yet")

    # Sections with students but no timetable
    for section in Section.query.filter(Section.class_id.isnot(None)).all():
        has_students = Student.query.filter_by(section_id=section.id).count() > 0
        has_periods = TimetablePeriod.query.filter_by(section_id=section.id).count() > 0
        if has_students and not has_periods:
            warnings.append(f"{section.full_name()} has students but no timetable")

    return errors, warnings


def publish_timetable(admin_name):
    """Send the draft to everyone: teachers and students see this version from now on."""
    errors, warnings = check_draft_problems()
    if len(errors) > 0:
        return jsonify({"message": "Fix these clashes before publishing", "status": "failed", "errors": errors}), 409

    if TimetablePeriod.query.count() == 0:
        return jsonify({"message": "The timetable is empty; add some periods before publishing", "status": "failed"}), 400

    version = TimetableVersion(
        published_at=pakistan_time(),
        published_by=admin_name,
        days=days_text(get_school_days()),
        periods_json=json.dumps(get_period_rows()),
        draft_signature=draft_signature()
    )
    db.session.add(version)
    db.session.flush()

    for timetable_period in TimetablePeriod.query.all():
        teacher = get_period_teacher(timetable_period.section_id, timetable_period.subject_id)
        db.session.add(PublishedPeriod(
            version_id=version.id,
            section_id=timetable_period.section_id,
            day=timetable_period.day,
            period=timetable_period.period,
            subject_id=timetable_period.subject_id,
            subject_name=timetable_period.subject.name,
            teacher_id=teacher.id if teacher else None,
            teacher_name=teacher.name if teacher else None,
            section_name=timetable_period.section.full_name()
        ))
    db.session.commit()

    return jsonify({"message": "Timetable published. Teachers and students can see it now.", "status": "success",
                    "warnings": warnings, "publish_status": publish_status()})


def get_publish_check():
    """What publishing now would report, without publishing."""
    errors, warnings = check_draft_problems()
    return jsonify({"errors": errors, "warnings": warnings, "status": publish_status()})


# ---------------- The published timetable (what teachers and students see)

def published_layout(version):
    period_rows = json.loads(version.periods_json)
    days = []
    for part in version.days.split(","):
        if part.strip() != "":
            days.append(int(part))
    return {
        "days": day_list(days),
        "periods": period_rows,
        "periods_per_day": class_period_count(period_rows)
    }


def published_slot_data(row):
    return {
        "id": row.id,
        "section_id": row.section_id,
        "section_name": row.section_name,
        "day": row.day,
        "day_name": DAY_NAMES.get(row.day, str(row.day)),
        "period": row.period,
        "subject_id": row.subject_id,
        "subject_name": row.subject_name,
        "teacher_id": row.teacher_id,
        "teacher_name": row.teacher_name
    }


def not_published_answer():
    data = layout_data()
    data["is_published"] = False
    data["published_at"] = None
    data["slots"] = []
    return jsonify(data)


def get_published_section_timetable(section_id):
    version = latest_version()
    if not version:
        return not_published_answer()

    section = Section.query.get(section_id)
    slot_list = []
    for row in PublishedPeriod.query.filter_by(version_id=version.id, section_id=section_id).order_by(PublishedPeriod.day, PublishedPeriod.period).all():
        slot_list.append(published_slot_data(row))

    data = published_layout(version)
    data["is_published"] = True
    data["published_at"] = version.published_at.strftime("%Y-%m-%d %H:%M")
    data["section_id"] = section_id
    data["section_name"] = section.full_name() if section else None
    data["slots"] = slot_list
    return jsonify(data)


def get_published_teacher_timetable(teacher_id):
    """A teacher's own week from the published timetable: every period they teach, in any section."""
    version = latest_version()
    if not version:
        return not_published_answer()

    slot_list = []
    for row in PublishedPeriod.query.filter_by(version_id=version.id, teacher_id=teacher_id).order_by(PublishedPeriod.day, PublishedPeriod.period).all():
        slot_list.append(published_slot_data(row))

    data = published_layout(version)
    data["is_published"] = True
    data["published_at"] = version.published_at.strftime("%Y-%m-%d %H:%M")
    data["slots"] = slot_list
    return jsonify(data)


def get_published_info():
    """When the timetable was last published (for the notification bell)."""
    version = latest_version()
    if not version:
        return jsonify({"is_published": False, "published_at": None, "version_id": None})
    return jsonify({"is_published": True, "published_at": version.published_at.strftime("%Y-%m-%d %H:%M"), "version_id": version.id})
