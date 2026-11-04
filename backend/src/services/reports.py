from io import BytesIO
from flask import send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from src.services.daily_attendance import get_section_month_summary
from src.services.exam_results import get_section_result_sheet
from src.services.oversight import syllabus_coverage_rows, get_teachers_overview, low_attendance_rows, search_activity_log


# Reports the admin can download as Excel files. They use the same data as the
# pages, so a download always matches what is on screen. (For PDF, each report
# page has a Print button: the browser can save the page as a PDF.)

EXCEL_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
HEADER_FILL = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")


def make_excel_file(title, headers, rows, file_name, notes=None):
    """One sheet: an optional title and notes, a bold header row, then the rows."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = title[:31]          # Excel allows 31 characters

    sheet.append([title])
    sheet["A1"].font = Font(bold=True, size=14)
    if notes:
        for note in notes:
            sheet.append([note])
    sheet.append([])

    sheet.append(headers)
    header_row = sheet.max_row
    for cell in sheet[header_row]:
        cell.font = Font(bold=True)
        cell.fill = HEADER_FILL

    for row in rows:
        sheet.append(row)

    # Make each column wide enough for its longest value
    for column in sheet.columns:
        longest = 8
        for cell in column:
            if cell.row <= header_row - 1:
                continue      # the title and notes may be long; don't widen for them
            if cell.value is not None and len(str(cell.value)) > longest:
                longest = len(str(cell.value))
        sheet.column_dimensions[column[0].column_letter].width = min(longest + 2, 60)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return send_file(output, mimetype=EXCEL_TYPE, as_attachment=True, download_name=file_name)


def read_service_answer(answer):
    """A service answer (a response, or (response, status)) as (data, error answer)."""
    status_code = 200
    response = answer
    if isinstance(answer, tuple):
        response = answer[0]
        status_code = answer[1]
    if status_code != 200:
        return None, (response, status_code)
    return response.get_json(), None


def empty_text(value):
    if value is None:
        return "-"
    return value


# ---------------- The reports

def attendance_report(section_id, year, month):
    data, error = read_service_answer(get_section_month_summary(section_id, year, month))
    if error:
        return error

    rows = []
    for student in data["students"]:
        rows.append([empty_text(student["roll_number"]), student["name"], student["present"], student["absent"],
                     student["late"], student["leave"], empty_text(student["percentage"])])
    headers = ["Roll No.", "Name", "Present", "Absent", "Late", "Leave", "Attendance %"]
    title = f"Attendance {data['section_name']} {data['month']}"
    file_name = f"attendance-{data['section_name']}-{data['month']}.xlsx".replace(" ", "")
    return make_excel_file(title, headers, rows, file_name, ["Late counts as attended; leave is not counted."])


def results_report(term_id, section_id):
    data, error = read_service_answer(get_section_result_sheet(term_id, section_id))
    if error:
        return error

    headers = ["Roll No.", "Name"]
    for subject in data["subjects"]:
        headers.append(f"{subject['subject_name']} ({subject['total_marks']})")
    headers = headers + ["Total", "Percentage", "Grade", "Position", "Result"]

    rows = []
    for student in data["students"]:
        row = [empty_text(student["roll_number"]), student["name"]]
        for subject in student["subjects"]:
            if subject["is_absent"]:
                row.append("Absent")
            else:
                row.append(empty_text(subject["obtained_marks"]))
        row = row + [f"{student['total_obtained']}/{student['total_marks']}", empty_text(student["percentage"]),
                     empty_text(student["grade"]), empty_text(student["position"]), student["result"]]
        rows.append(row)

    term = data["term"]
    title = f"Results {data['section_name']} {term['name']} {term['session_name']}"
    notes = [f"{data['passed_count']} of {len(data['students'])} students passed"]
    file_name = f"results-{data['section_name']}-{term['name']}.xlsx".replace(" ", "")
    return make_excel_file(title, headers, rows, file_name, notes)


def syllabus_report():
    rows = []
    for school_class in syllabus_coverage_rows():
        for section in school_class["sections"]:
            for subject in section["subjects"]:
                rows.append([section["section_name"], subject["subject_name"], empty_text(subject["teacher_name"]),
                             subject["chapters_done"], subject["chapter_count"], subject["percentage"]])
    headers = ["Section", "Subject", "Teacher", "Chapters done", "Chapters", "Covered %"]
    return make_excel_file("Syllabus coverage", headers, rows, "syllabus-coverage.xlsx")


def teachers_report():
    data, error = read_service_answer(get_teachers_overview())
    if error:
        return error

    rows = []
    for teacher in data["teachers"]:
        week = teacher["this_week"]
        incharge_text = "-"
        if len(teacher["incharge_of"]) > 0:
            incharge_text = ", ".join(teacher["incharge_of"])
        rows.append([teacher["name"], teacher["username"], empty_text(teacher["last_login"]), empty_text(teacher["last_active"]),
                     incharge_text, teacher["subjects_taught"], week["attendance_days_marked"],
                     week["diary_entries"], week["assignments"], week["class_tests"], week["progress_updates"],
                     week["actions"], teacher["papers_pending"]])
    headers = ["Teacher", "Username", "Last login", "Last active", "Class incharge of", "Subjects taught",
               "Attendance days marked", "Diary entries", "Assignments", "Class tests", "Syllabus updates",
               "Actions", "Papers with marks missing"]
    notes = [f"Activity from {data['week_start']} to {data['today']}"]
    return make_excel_file("Teacher activity", headers, rows, "teacher-activity.xlsx", notes)


def low_attendance_report():
    rows = []
    for student in low_attendance_rows():
        rows.append([empty_text(student["section_name"]), empty_text(student["roll_number"]), student["name"],
                     student["percentage"], student["absent"], student["days_counted"]])
    headers = ["Section", "Roll No.", "Name", "Attendance %", "Days absent", "Days counted"]
    return make_excel_file("Low attendance", headers, rows, "low-attendance.xlsx")


def activity_report(filters):
    # Up to the 5000 newest matching entries
    data, error = read_service_answer(search_activity_log(filters, 1, 5000))
    if error:
        return error

    rows = []
    for entry in data["entries"]:
        rows.append([entry["created_at"], empty_text(entry["user_name"]), empty_text(entry["user_role"]),
                     entry["action"], entry["area"], entry["description"], empty_text(entry["ip_address"])])
    headers = ["Time", "Name", "Role", "Action", "Area", "What", "IP address"]
    notes = [f"{data['total']} matching entries (up to 5000 newest shown)"]
    return make_excel_file("Activity log", headers, rows, "activity-log.xlsx", notes)

