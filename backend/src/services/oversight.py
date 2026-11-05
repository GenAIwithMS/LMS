from datetime import datetime, timedelta
from flask import jsonify
from sqlalchemy.orm import joinedload
from src.db import db, pakistan_time
from src.models import (ActivityLog, Teacher, Student, Section, SchoolClass, Subject, SyllabusChapter, ChapterProgress,
                        TeachingAssignment, DailyAttendance, DiaryEntry, Assignment, ClassTest, ExamTerm, ExamPaper,
                        TimetablePeriod, AcademicSession)
from src.services.exam import term_is_closed
from src.services.daily_attendance import count_statuses


# Admin oversight: the activity log, what each teacher has been doing, and a dashboard
# of what needs attention today (attendance not marked, marks not entered, syllabus
# behind, students who are often absent).

WEEK_DAYS = 7                  # "this week" means the last 7 days
LOW_ATTENDANCE_PERCENT = 75    # students below this are flagged


def today():
    return pakistan_time().date()


def week_start():
    return today() - timedelta(days=WEEK_DAYS - 1)


def time_text(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M")


# ---------------- Activity log

def log_data(entry):
    return {
        "id": entry.id,
        "created_at": time_text(entry.created_at),
        "user_role": entry.user_role,
        "user_id": entry.user_id,
        "user_name": entry.user_name,
        "action": entry.action,
        "area": entry.area,
        "description": entry.description,
        "ip_address": entry.ip_address,
        "section_id": entry.section_id,
        "class_id": entry.class_id
    }


def search_activity_log(filters, page=1, per_page=50):
    """The activity log, newest first. filters can hold: name (part of the person's name),
    role, user_id, action, area, class_id, section_id, date_from and date_to (dates)."""
    query = ActivityLog.query

    if filters.get("name"):
        query = query.filter(ActivityLog.user_name.ilike("%" + filters["name"].strip() + "%"))
    if filters.get("role"):
        query = query.filter(ActivityLog.user_role == filters["role"])
    if filters.get("user_id"):
        query = query.filter(ActivityLog.user_id == filters["user_id"])
    if filters.get("action"):
        query = query.filter(ActivityLog.action == filters["action"])
    if filters.get("area"):
        query = query.filter(ActivityLog.area == filters["area"])
    if filters.get("class_id"):
        query = query.filter(ActivityLog.class_id == filters["class_id"])
    if filters.get("section_id"):
        query = query.filter(ActivityLog.section_id == filters["section_id"])
    if filters.get("date_from"):
        query = query.filter(ActivityLog.created_at >= datetime.combine(filters["date_from"], datetime.min.time()))
    if filters.get("date_to"):
        # Up to the end of that day
        day_after = filters["date_to"] + timedelta(days=1)
        query = query.filter(ActivityLog.created_at < datetime.combine(day_after, datetime.min.time()))

    total = query.count()
    entries = query.order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    entry_list = []
    for entry in entries:
        entry_list.append(log_data(entry))

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "entries": entry_list
    })


def get_log_areas():
    """The areas that appear in the log, for the filter list."""
    areas = []
    for row in ActivityLog.query.with_entities(ActivityLog.area).distinct().all():
        areas.append(row[0])
    areas.sort()
    return areas


# ---------------- Teachers

def last_activity(teacher_id, action=None):
    query = ActivityLog.query.filter_by(user_role="teacher", user_id=teacher_id)
    if action:
        query = query.filter_by(action=action)
    entry = query.order_by(ActivityLog.created_at.desc()).first()
    if entry:
        return time_text(entry.created_at)
    return None


def section_is_marked(section_id, day):
    """True when every student of the section has attendance for this day."""
    student_count = Student.query.filter_by(section_id=section_id).count()
    if student_count == 0:
        return True
    marked = DailyAttendance.query.filter_by(section_id=section_id, date=day).count()
    return marked >= student_count


def open_terms():
    """Exam terms that have started and whose marks can still be entered."""
    term_list = []
    for term in ExamTerm.query.all():
        if term.start_date <= today() and not term_is_closed(term):
            term_list.append(term)
    return term_list


def pending_marks_for_teaching(teaching):
    """For one teaching assignment: the open papers where marks are still missing."""
    pending = []
    student_ids = []
    for student in Student.query.filter_by(section_id=teaching.section_id).all():
        student_ids.append(student.id)
    if len(student_ids) == 0:
        return pending

    for term in open_terms():
        paper = ExamPaper.query.filter_by(term_id=term.id, subject_id=teaching.subject_id).first()
        if not paper:
            continue
        entered = 0
        for mark in paper.marks:
            if mark.student_id in student_ids:
                entered = entered + 1
        if entered < len(student_ids):
            pending.append({
                "term_name": term.name,
                "subject_name": paper.subject.name,
                "section_name": teaching.section.full_name(),
                "entered": entered,
                "student_count": len(student_ids)
            })
    return pending


def chapter_coverage(section_id, subject_id):
    """(done chapters, all chapters) of a subject in a section."""
    chapters = SyllabusChapter.query.filter_by(subject_id=subject_id).all()
    done = 0
    for chapter in chapters:
        progress = ChapterProgress.query.filter_by(section_id=section_id, chapter_id=chapter.id).first()
        if progress and progress.status == "done":
            done = done + 1
    return done, len(chapters)


def teacher_week_counts(teacher_id):
    """What a teacher did in the last 7 days."""
    start = week_start()
    start_time = datetime.combine(start, datetime.min.time())

    diary_count = DiaryEntry.query.filter(DiaryEntry.teacher_id == teacher_id, DiaryEntry.date >= start).count()
    assignment_count = Assignment.query.filter(Assignment.teacher_id == teacher_id, Assignment.created_at >= start_time).count()
    test_count = ClassTest.query.filter(ClassTest.teacher_id == teacher_id, ClassTest.date >= start).count()
    progress_count = ChapterProgress.query.filter(ChapterProgress.updated_by == teacher_id, ChapterProgress.updated_at >= start_time).count()

    attendance_days = []
    for record in DailyAttendance.query.filter(DailyAttendance.marked_by == teacher_id, DailyAttendance.date >= start).all():
        if record.date not in attendance_days:
            attendance_days.append(record.date)

    action_count = ActivityLog.query.filter(ActivityLog.user_role == "teacher", ActivityLog.user_id == teacher_id,
                                            ActivityLog.created_at >= start_time).count()
    return {
        "diary_entries": diary_count,
        "assignments": assignment_count,
        "class_tests": test_count,
        "progress_updates": progress_count,
        "attendance_days_marked": len(attendance_days),
        "actions": action_count
    }


def teacher_summary(teacher):
    incharge_sections = Section.query.filter_by(teacher_id=teacher.id).all()
    teachings = TeachingAssignment.query.filter_by(teacher_id=teacher.id).all()

    not_marked_today = []
    for section in incharge_sections:
        if not section_is_marked(section.id, today()):
            not_marked_today.append(section.full_name())

    pending_count = 0
    for teaching in teachings:
        pending_count = pending_count + len(pending_marks_for_teaching(teaching))

    incharge_names = []
    for section in incharge_sections:
        incharge_names.append(section.full_name())

    return {
        "id": teacher.id,
        "name": teacher.name,
        "username": teacher.username,
        "email": teacher.email,
        "last_login": last_activity(teacher.id, "login"),
        "last_active": last_activity(teacher.id),
        "incharge_of": incharge_names,
        "subjects_taught": len(teachings),
        "this_week": teacher_week_counts(teacher.id),
        "attendance_not_marked_today": not_marked_today,
        "papers_pending": pending_count
    }


def get_teachers_overview():
    teacher_list = []
    for teacher in Teacher.query.order_by(Teacher.name).all():
        teacher_list.append(teacher_summary(teacher))
    return jsonify({
        "week_start": week_start().isoformat(),
        "today": today().isoformat(),
        "teachers": teacher_list
    })


def get_teacher_activity(teacher_id):
    """Everything about one teacher's work: classes, syllabus progress, this week's
    diary and assignments, marks still to enter, and their recent actions."""
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found", "status": "failed"}), 404

    data = teacher_summary(teacher)

    teaching_list = []
    pending_list = []
    period_count = 0
    for teaching in TeachingAssignment.query.filter_by(teacher_id=teacher.id).all():
        done, total = chapter_coverage(teaching.section_id, teaching.subject_id)
        percentage = 0
        if total > 0:
            percentage = round(done * 100 / total)
        periods = TimetablePeriod.query.filter_by(section_id=teaching.section_id, subject_id=teaching.subject_id).count()
        period_count = period_count + periods
        teaching_list.append({
            "section_id": teaching.section_id,
            "section_name": teaching.section.full_name(),
            "subject_name": teaching.subject.name,
            "chapters_done": done,
            "chapter_count": total,
            "percentage": percentage,
            "periods_per_week": periods
        })
        for item in pending_marks_for_teaching(teaching):
            pending_list.append(item)
    teaching_list.sort(key=lambda item: (item["section_name"], item["subject_name"]))

    start = week_start()
    start_time = datetime.combine(start, datetime.min.time())
    diary_list = []
    for entry in DiaryEntry.query.filter(DiaryEntry.teacher_id == teacher.id, DiaryEntry.date >= start).order_by(DiaryEntry.date.desc()).all():
        diary_list.append({
            "date": entry.date.isoformat(),
            "section_name": entry.section.full_name(),
            "subject_name": entry.subject.name,
            "classwork": entry.classwork,
            "homework": entry.homework
        })

    assignment_list = []
    for assignment in Assignment.query.filter(Assignment.teacher_id == teacher.id, Assignment.created_at >= start_time).order_by(Assignment.created_at.desc()).all():
        assignment_list.append({
            "title": assignment.title,
            "subject_name": assignment.subject.name,
            "section_name": assignment.section.full_name() if assignment.section else None,
            "due_date": assignment.due_date.isoformat(),
            "created_at": time_text(assignment.created_at)
        })

    recent = []
    entries = ActivityLog.query.filter_by(user_role="teacher", user_id=teacher.id).order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc()).limit(30).all()
    for entry in entries:
        recent.append(log_data(entry))

    data["teaching"] = teaching_list
    data["periods_per_week"] = period_count
    data["marks_pending"] = pending_list
    data["diary_this_week"] = diary_list
    data["assignments_this_week"] = assignment_list
    data["recent_actions"] = recent
    return jsonify(data)


# ---------------- Dashboard

# ---------------- Loading in bulk
# The dashboard covers the whole school, so each kind of data is loaded once and then
# looked up in memory, instead of one database query per section, subject or student.

def students_by_section():
    """{section_id: [student ids]} for every student."""
    result = {}
    for student_id, section_id in db.session.query(Student.id, Student.section_id).all():
        if section_id not in result:
            result[section_id] = []
        result[section_id].append(student_id)
    return result


def teacher_names_by_teaching():
    """{(section_id, subject_id): teacher name} for every subject teacher."""
    result = {}
    rows = db.session.query(TeachingAssignment.section_id, TeachingAssignment.subject_id, Teacher.name).join(
        Teacher, Teacher.id == TeachingAssignment.teacher_id).all()
    for section_id, subject_id, name in rows:
        result[(section_id, subject_id)] = name
    return result


def attendance_today_rows():
    """Every section (in a class) with today's attendance numbers."""
    rows = []
    sections = Section.query.options(joinedload(Section.school_class), joinedload(Section.teacher)).filter(Section.class_id.isnot(None)).all()
    sections.sort(key=lambda section: (section.school_class.level, section.name))
    student_ids = students_by_section()
    records_by_section = {}
    for record in DailyAttendance.query.filter_by(date=today()).all():
        if record.section_id not in records_by_section:
            records_by_section[record.section_id] = []
        records_by_section[record.section_id].append(record)
    for section in sections:
        student_count = len(student_ids.get(section.id, []))
        records = records_by_section.get(section.id, [])
        counts = count_statuses(records)
        rows.append({
            "section_id": section.id,
            "section_name": section.full_name(),
            "incharge_name": section.teacher.name if section.teacher else None,
            "student_count": student_count,
            "marked_count": len(records),
            "is_marked": student_count > 0 and len(records) >= student_count,
            "present": counts["present"],
            "absent": counts["absent"],
            "late": counts["late"],
            "leave": counts["leave"]
        })
    return rows


def syllabus_coverage_rows():
    """For each class: each section's coverage per subject, and the averages."""
    class_list = []
    # Everything needed, loaded once
    all_sections = Section.query.filter(Section.class_id.isnot(None)).order_by(Section.name).all()
    all_subjects = Subject.query.filter(Subject.class_id.isnot(None)).order_by(Subject.name).all()
    chapters_by_subject = {}
    for chapter_id, subject_id in db.session.query(SyllabusChapter.id, SyllabusChapter.subject_id).all():
        if subject_id not in chapters_by_subject:
            chapters_by_subject[subject_id] = []
        chapters_by_subject[subject_id].append(chapter_id)
    done_chapters = set()
    for section_id, chapter_id in db.session.query(ChapterProgress.section_id, ChapterProgress.chapter_id).filter(ChapterProgress.status == "done").all():
        done_chapters.add((section_id, chapter_id))
    teacher_names = teacher_names_by_teaching()

    for school_class in SchoolClass.query.order_by(SchoolClass.level).all():
        sections = [section for section in all_sections if section.class_id == school_class.id]
        subjects = [subject for subject in all_subjects if subject.class_id == school_class.id]
        if len(sections) == 0 or len(subjects) == 0:
            continue

        section_list = []
        class_percentages = []
        for section in sections:
            subject_list = []
            section_percentages = []
            for subject in subjects:
                chapter_ids = chapters_by_subject.get(subject.id, [])
                total = len(chapter_ids)
                if total == 0:
                    continue
                done = 0
                for chapter_id in chapter_ids:
                    if (section.id, chapter_id) in done_chapters:
                        done = done + 1
                percentage = round(done * 100 / total)
                section_percentages.append(percentage)
                subject_list.append({
                    "subject_name": subject.name,
                    "teacher_name": teacher_names.get((section.id, subject.id)),
                    "chapters_done": done,
                    "chapter_count": total,
                    "percentage": percentage
                })

            average = None
            if len(section_percentages) > 0:
                average = round(sum(section_percentages) / len(section_percentages))
                class_percentages.append(average)
            section_list.append({
                "section_id": section.id,
                "section_name": section.full_name(),
                "average_percentage": average,
                "subjects": subject_list
            })

        class_average = None
        if len(class_percentages) > 0:
            class_average = round(sum(class_percentages) / len(class_percentages))
        class_list.append({
            "class_id": school_class.id,
            "class_name": school_class.name,
            "average_percentage": class_average,
            "sections": section_list
        })
    return class_list


def marks_entry_rows():
    """Every open paper in every section where marks are still missing."""
    rows = []
    terms = open_terms()
    if len(terms) == 0:
        return rows
    students = students_by_section()
    teacher_names = teacher_names_by_teaching()
    all_sections = Section.query.filter(Section.class_id.isnot(None)).order_by(Section.name).all()
    for term in terms:
        for paper in ExamPaper.query.filter_by(term_id=term.id).all():
            for section in [section for section in all_sections if section.class_id == paper.class_id]:
                student_ids = students.get(section.id, [])
                if len(student_ids) == 0:
                    continue
                entered = 0
                for mark in paper.marks:
                    if mark.student_id in student_ids:
                        entered = entered + 1
                if entered >= len(student_ids):
                    continue
                rows.append({
                    "term_name": term.name,
                    "section_name": section.full_name(),
                    "subject_name": paper.subject.name,
                    "teacher_name": teacher_names.get((section.id, paper.subject_id)),
                    "entered": entered,
                    "student_count": len(student_ids)
                })
    return rows


def low_attendance_rows(threshold=LOW_ATTENDANCE_PERCENT):
    """Students whose attendance this session is below the threshold, lowest first."""
    session = AcademicSession.query.filter_by(is_current=True).first()
    rows = []
    # All of this session's attendance in one query, grouped by student
    query = DailyAttendance.query
    if session:
        query = query.filter(DailyAttendance.date >= session.start_date, DailyAttendance.date <= session.end_date)
    records_by_student = {}
    for record in query.all():
        if record.student_id not in records_by_student:
            records_by_student[record.student_id] = []
        records_by_student[record.student_id].append(record)

    students = Student.query.options(joinedload(Student.section).joinedload(Section.school_class)).all()
    for student in students:
        records = records_by_student.get(student.id, [])
        counts = count_statuses(records)
        if counts["percentage"] is None or counts["percentage"] >= threshold:
            continue
        rows.append({
            "student_id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "section_name": student.section.full_name() if student.section else None,
            "percentage": counts["percentage"],
            "absent": counts["absent"],
            "days_counted": counts["present"] + counts["late"] + counts["absent"]
        })
    rows.sort(key=lambda row: row["percentage"])
    return rows


def get_oversight_dashboard():
    attendance = attendance_today_rows()
    marked = 0
    for row in attendance:
        if row["is_marked"]:
            marked = marked + 1

    waiting_papers = ExamPaper.query.filter_by(question_status="submitted").count()

    return jsonify({
        "today": today().isoformat(),
        "low_attendance_percent": LOW_ATTENDANCE_PERCENT,
        "counts": {
            "students": Student.query.count(),
            "teachers": Teacher.query.count(),
            "sections": len(attendance),
            "sections_marked_today": marked,
            "question_papers_waiting": waiting_papers
        },
        "attendance_today": attendance,
        "syllabus_coverage": syllabus_coverage_rows(),
        "marks_pending": marks_entry_rows(),
        "low_attendance": low_attendance_rows()
    })
