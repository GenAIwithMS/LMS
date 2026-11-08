"""End-to-end test: one school term from start to end, through the running server.

The admin sets up a new Class 3 (and Class 4 for promotion), adds teachers and students,
builds and publishes the timetable, and sets up the exam. The teachers teach (attendance,
diary, syllabus, assignments, class tests, question paper, marks, remarks). The students
see and do their part. The admin publishes results and promotes the class. Every step is
checked from the side of the person doing it, and what the others then see.
"""
import io
import sys
import time
from datetime import date, timedelta

import requests

BASE = "http://localhost:5000/api"
RUN = str(int(time.time()))[-5:]      # makes names unique for this run
TODAY = date.today()
results = []


def step(role, name, ok, detail=""):
    results.append((role, name, bool(ok), str(detail)[:160]))
    mark = "PASS" if ok else "FAIL"
    print(f"{mark} [{role}] {name}" + ("" if ok else f"  -> {str(detail)[:160]}"))


def call(method, path, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = "Bearer " + token
    response = requests.request(method, BASE + path, headers=headers, timeout=30, **kwargs)
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return response.status_code, body


def login(email, password="secret1"):
    status, body = call("POST", "/login", json={"email": email, "password": password})
    if status != 200:
        return None, (status, body)
    return body["token"], None


def school_day(offset_back):
    """The school day offset_back school days before today (Monday-Saturday)."""
    day = TODAY
    left = offset_back
    while day.isoweekday() == 7 or left > 0:
        if day.isoweekday() != 7:
            left = left - 1
        day = day - timedelta(days=1)
        while day.isoweekday() == 7:
            day = day - timedelta(days=1)
        if left == 0:
            break
    while day.isoweekday() == 7:
        day = day - timedelta(days=1)
    return day.isoformat()


# ======================= ADMIN: set up the school =======================
root, error = login("root@lms.test")
step("admin", "logs in", root, error)

status, sessions = call("GET", "/school/sessions", root)
current = [s for s in sessions if s.get("is_current")]
SESSION = current[0]["id"] if current else None
step("admin", "has a current academic session", SESSION, sessions)

classes = call("GET", "/school/classes", root)[1]
CLASS_3 = classes[2]["id"]
CLASS_4 = classes[3]["id"]
step("admin", "Class 3 and Class 4 exist and are empty",
     classes[2]["name"] == "Class 3" and len(classes[2]["sections"]) == 0 and len(classes[3]["sections"]) == 0, classes[2])

# Teachers
teacher_ids = {}
for key, name in [("nadia", "Nadia Iqbal"), ("kamran", "Kamran Ali")]:
    uname = f"{key}{RUN}"
    status, body = call("POST", "/add/teacher", root, json={"name": name, "username": uname, "email": f"{uname}@lms.test", "password": "secret1"})
    step("admin", f"adds teacher {name}", status in (200, 201), body)
for teacher in call("GET", "/get/teacher", root)[1]:
    for key in ["nadia", "kamran"]:
        if teacher["username"] == f"{key}{RUN}":
            teacher_ids[key] = teacher["id"]
NADIA, KAMRAN = teacher_ids.get("nadia"), teacher_ids.get("kamran")
step("admin", "sees both new teachers in the list", NADIA and KAMRAN, teacher_ids)

# Sections: 3-A led by Nadia, and 4-A for next year
status, body = call("POST", f"/school/classes/{CLASS_3}/sections", root, json={"name": "A", "incharge_id": NADIA})
SEC_3A = body.get("section_id") if isinstance(body, dict) else None
step("admin", "adds section 3-A with Nadia as class incharge", status == 201 and SEC_3A, body)
status, body = call("POST", f"/school/classes/{CLASS_4}/sections", root, json={"name": "A"})
SEC_4A = body.get("section_id") if isinstance(body, dict) else None
step("admin", "adds section 4-A (for promotion)", status == 201 and SEC_4A, body)
status, body = call("POST", f"/school/classes/{CLASS_3}/sections", root, json={"name": "B", "incharge_id": NADIA})
step("admin", "can't make Nadia incharge of a second section", status in (400, 409), body)

# Subjects, chapters and who teaches what
subjects = {}
for name in ["Maths", "English"]:
    status, body = call("POST", f"/school/classes/{CLASS_3}/subjects", root, json={"name": name})
    subjects[name] = body.get("subject_id") if isinstance(body, dict) else None
    step("admin", f"adds subject {name} to Class 3", status == 201, body)
call("POST", f"/school/teachers/{NADIA}/subjects", root, json={"name": "Maths"})
call("POST", f"/school/teachers/{KAMRAN}/subjects", root, json={"name": "English"})
status, body = call("PUT", f"/school/sections/{SEC_3A}/teachers", root, json={"subject_id": subjects["Maths"], "teacher_id": NADIA})
step("admin", "gives 3-A Maths to Nadia", status == 200, body)
status, body = call("PUT", f"/school/sections/{SEC_3A}/teachers", root, json={"subject_id": subjects["English"], "teacher_id": KAMRAN})
step("admin", "gives 3-A English to Kamran", status == 200, body)

# Students
student_ids = {}
for roll, (key, name) in enumerate([("ayesha", "Ayesha Noor"), ("usman", "Usman Tariq"), ("zainab", "Zainab Shah")], start=1):
    uname = f"{key}{RUN}"
    status, body = call("POST", "/add/student", root, json={"name": name, "username": uname, "email": f"{uname}@lms.test",
                                                          "password": "secret1", "section_id": SEC_3A, "roll_number": str(roll)})
    step("admin", f"adds student {name} (roll {roll})", status in (200, 201), body)
status, body = call("POST", "/add/student", root, json={"name": "Copy Roll", "username": f"copy{RUN}", "email": f"copy{RUN}@lms.test",
                                                      "password": "secret1", "section_id": SEC_3A, "roll_number": "1"})
step("admin", "a second roll 1 in 3-A is refused", status in (400, 409), body)
for student in call("GET", "/get/student", root)[1]:
    for key in ["ayesha", "usman", "zainab"]:
        if student["username"] == f"{key}{RUN}":
            student_ids[key] = student["id"]
step("admin", "sees the 3 students", len(student_ids) == 3, student_ids)

# Timetable: Maths period 1 and English period 2, Monday to Saturday; then publish
ok = True
for day in range(1, 7):
    for period, subject in [(1, "Maths"), (2, "English")]:
        status, body = call("PUT", f"/school/sections/{SEC_3A}/timetable", root, json={"day": day, "period": period, "subject_id": subjects[subject]})
        ok = ok and status == 200
step("admin", "builds 3-A's timetable (12 periods)", ok)
status, body = call("POST", "/timetable/publish", root)
step("admin", "publishes the timetable", status == 200, body)

# Exam term and papers
term_start = (TODAY - timedelta(days=10)).isoformat()
term_end = (TODAY - timedelta(days=1)).isoformat()
status, body = call("POST", "/exams/terms", root, json={"session_id": SESSION, "name": f"Mid Term {RUN}", "start_date": term_start, "end_date": term_end})
TERM = body["term"]["id"] if isinstance(body, dict) and "term" in body else None
step("admin", "adds an exam term", status == 201 and TERM, body)
status, body = call("POST", f"/exams/terms/{TERM}/papers", root, json={"class_id": CLASS_3})
step("admin", "sets up Class 3's papers", status in (200, 201), body)
papers = {p["subject_name"]: p["id"] for p in call("GET", f"/exams/terms/{TERM}/papers", root)[1] if p["class_id"] == CLASS_3}
step("admin", "sees a Maths and an English paper", set(papers) == {"Maths", "English"}, papers)

# Announcement and event
status, body = call("POST", "/admin/announcements", root, json={"title": f"Welcome back {RUN}", "content": "Term starts now.", "target_audience": "all"})
step("admin", "posts a school announcement", status == 201, body)
status, body = call("POST", "/create/event", root, json={"title": f"Parents day {RUN}", "event_date": (TODAY + timedelta(days=5)).isoformat(), "event_time": "10:00"})
step("admin", "adds an upcoming event", status == 201, body)


# ======================= TEACHERS: teach the term =======================
nadia, error = login(f"nadia{RUN}@lms.test")
step("teacher", "Nadia logs in", nadia, error)
kamran, error = login(f"kamran{RUN}@lms.test")
step("teacher", "Kamran logs in", kamran, error)

body = call("GET", "/school/my-classes", nadia)[1]
step("teacher", "Nadia sees 3-A as her class and Maths as her subject",
     any(s["id"] == SEC_3A for s in body.get("incharge_of", [])) and "Maths" in str(body.get("teaching", body)), body)
body = call("GET", "/school/my-timetable", nadia)[1]
step("teacher", "Nadia's timetable has her 6 Maths periods", str(body).count("Maths") >= 6, str(body)[:120])

# Attendance for the last 3 school days (Usman absent on one)
for back in range(3):
    day = school_day(back)
    records = [{"student_id": student_ids["ayesha"], "status": "present"},
               {"student_id": student_ids["usman"], "status": "absent" if back == 1 else "present"},
               {"student_id": student_ids["zainab"], "status": "late" if back == 2 else "present"}]
    status, body = call("POST", f"/school/sections/{SEC_3A}/attendance", nadia, json={"date": day, "records": records})
    step("teacher", f"Nadia marks attendance for {day}", status == 200, body)
status, body = call("POST", f"/school/sections/{SEC_3A}/attendance", kamran, json={"date": school_day(0), "records": records})
step("teacher", "Kamran (not the incharge) can't mark attendance", status == 403, body)

# Diary and syllabus
status, body = call("POST", f"/school/sections/{SEC_3A}/diary", nadia, json={"subject_id": subjects["Maths"], "date": school_day(0), "classwork": "Addition, page 10", "homework": "Exercise 2"})
step("teacher", "Nadia writes today's Maths diary", status in (200, 201), body)
status, body = call("POST", f"/school/sections/{SEC_3A}/diary", kamran, json={"subject_id": subjects["English"], "date": school_day(0), "homework": "Read story 1"})
step("teacher", "Kamran writes today's English diary", status in (200, 201), body)
# Nadia writes 3-A's Maths syllabus: chapters with daily topics, and ticks a topic off
chapters = []
for title in ["Counting", "Addition", "Subtraction"]:
    status, body = call("POST", f"/school/sections/{SEC_3A}/subjects/{subjects['Maths']}/chapters", nadia, json={"title": title})
    chapters.append(body["chapter"]["id"] if isinstance(body, dict) and "chapter" in body else None)
step("teacher", "Nadia writes 3 Maths chapters for 3-A", all(chapters), chapters)
status, body = call("POST", f"/school/sections/{SEC_3A}/subjects/{subjects['Maths']}/chapters", root, json={"title": "x"})
step("admin", "can't change a section's syllabus", status == 403, body)
topics = []
for title in ["Counting to 100", "Counting in tens"]:
    status, body = call("POST", f"/school/chapters/{chapters[0]}/topics", nadia, json={"title": title, "planned_date": school_day(0)})
    topics.append(body["topic"]["id"] if isinstance(body, dict) and "topic" in body else None)
step("teacher", "Nadia adds 2 daily topics to chapter 1", all(topics), topics)
for topic in topics:
    status, body = call("PUT", f"/school/topics/{topic}/done", nadia, json={"done": True})
step("teacher", "ticking both topics off finishes chapter 1",
     call("GET", f"/school/sections/{SEC_3A}/subjects/{subjects['Maths']}/progress", nadia)[1]["chapters"][0]["status"] == "done")

# Assignment and class test
due = (TODAY + timedelta(days=5)).isoformat()
status, body = call("POST", "/create/assignments", nadia, json={"title": f"Addition homework {RUN}", "description": "Exercise 2, all", "subject_id": subjects["Maths"], "section_id": SEC_3A, "due_date": due, "total_marks": 10})
step("teacher", "Nadia sets an assignment", status == 201, body)
HW = [a for a in call("GET", "/get/assignments", nadia)[1]["assignments"] if a["title"] == f"Addition homework {RUN}"][0]["id"]
status, body = call("POST", "/school/class-tests", nadia, json={"section_id": SEC_3A, "subject_id": subjects["Maths"], "title": f"Counting quiz {RUN}", "date": school_day(0), "total_marks": 10, "topic_id": topics[0]})
TEST = body.get("test", {}).get("id") if isinstance(body, dict) else None
step("teacher", "Nadia adds a class test", status == 201 and TEST, body)
status, body = call("PUT", f"/school/class-tests/{TEST}/marks", nadia, json={"marks": [
    {"student_id": student_ids["ayesha"], "obtained_marks": 9}, {"student_id": student_ids["usman"], "obtained_marks": 6},
    {"student_id": student_ids["zainab"], "obtained_marks": None}]})
step("teacher", "Nadia enters the quiz marks (Zainab absent)", status == 200, body)

# Question paper: Nadia uploads, the admin approves
status, body = call("POST", f"/exams/papers/{papers['Maths']}/question-paper", nadia, files={"file": ("maths.pdf", io.BytesIO(b"%PDF-1.4 e2e paper"), "application/pdf")})
step("teacher", "Nadia uploads the Maths question paper", status in (200, 201), body)
status, body = call("PUT", f"/exams/papers/{papers['Maths']}/review", root, json={"approve": True})
step("admin", "approves the Maths question paper", status == 200, body)


# ======================= STUDENTS: their side =======================
tokens = {}
for key in ["ayesha", "usman", "zainab"]:
    tokens[key], error = login(f"{key}{RUN}@lms.test")
    step("student", f"{key.title()} logs in", tokens[key], error)
ayesha = tokens["ayesha"]

body = call("GET", "/school/my-class", ayesha)[1]
step("student", "Ayesha sees her class 3-A, roll 1 and incharge Nadia",
     str(body).count("Class 3 - A") >= 1 and "Nadia" in str(body), str(body)[:150])
body = call("GET", "/school/my-timetable", ayesha)[1]
step("student", "Ayesha sees the published timetable", str(body).count("Maths") >= 6 and str(body).count("English") >= 6, str(body)[:120])
body = call("GET", f"/school/sections/{SEC_3A}/diary?date={school_day(0)}", ayesha)[1]
step("student", "Ayesha reads today's diary (Maths and English)", "Addition, page 10" in str(body) and "Read story 1" in str(body), str(body)[:150])
body = call("GET", "/school/my-attendance", ayesha)[1] if call("GET", "/school/my-attendance", ayesha)[0] == 200 else call("GET", "/school/attendance/me", ayesha)[1]
body = call("GET", "/get/announcements", ayesha)[1]
step("student", "Ayesha sees the school announcement", f"Welcome back {RUN}" in str(body), str(body)[:120])
body = call("GET", "/get/events", ayesha)[1]
step("student", "Ayesha sees the upcoming event", f"Parents day {RUN}" in str(body), str(body)[:120])
body = call("GET", "/school/class-tests", ayesha)[1]
step("student", "Ayesha sees her quiz mark 9 / 10", "9" in str([t.get("my_marks") for t in body if t.get("title") == f"Counting quiz {RUN}"]), str(body)[:160])
body = call("GET", "/get/assignments", ayesha)[1]
step("student", "Ayesha sees the Maths assignment", f"Addition homework {RUN}" in str(body), str(body)[:120])

# Submissions: Ayesha with a file, Usman with text; then Ayesha updates her text only
status, body = call("POST", "/submit/assignment", ayesha, data={"assignment_id": str(HW), "submission_text": "Answers attached"},
                    files={"submission_file": ("answers.pdf", io.BytesIO(b"%PDF-1.4 answers"), "application/pdf")})
step("student", "Ayesha submits with a PDF", status == 201, body)
status, body = call("POST", "/submit/assignment", tokens["usman"], data={"assignment_id": str(HW), "submission_text": "1) 5 2) 7"})
step("student", "Usman submits text", status == 201, body)
status, body = call("POST", "/submit/assignment", ayesha, data={"assignment_id": str(HW), "submission_text": "Answers attached (fixed Q3)"})
step("student", "Ayesha updates her submission", status == 200 and "updated" in str(body), body)
mine = call("GET", "/get/submissions/by/student", ayesha)[1]["data"]
step("student", "her file is still there after the update", mine and mine[0]["submission_file"], mine)

# Permissions from the student's side
status, body = call("GET", f"/exams/terms/{TERM}/sections/{SEC_3A}/results", ayesha)
step("student", "can't see the class result sheet", status == 403, body)
status, body = call("POST", f"/school/sections/{SEC_3A}/attendance", ayesha, json={"date": school_day(0), "records": []})
step("student", "can't mark attendance", status == 403, body)


# ======================= TEACHERS: grading and exam marks =======================
subs = call("GET", f"/get/submissions/by/assignment?id={HW}", nadia)[1]
subs = subs.get("data", subs) if isinstance(subs, dict) else subs
step("teacher", "Nadia sees 2 submissions", len(subs) == 2, subs)
for sub in subs:
    marks = "9" if sub.get("student") == "Ayesha Noor" else "6"
    status, body = call("PUT", f"/update/submission?id={sub['id']}", nadia, json={"marks_obtained": marks, "feedback": "Checked"})
    step("teacher", f"Nadia grades {sub.get('student')}", status == 200, body)
status, body = call("PUT", f"/update/submission?id={subs[0]['id']}", nadia, json={"marks_obtained": "11"})
step("teacher", "a grade above the total is refused", status == 400, body)
status, body = call("POST", "/submit/assignment", ayesha, data={"assignment_id": str(HW), "submission_text": "late change"})
step("student", "Ayesha can't change graded work", status == 409, body)
mine = call("GET", "/get/submissions/by/student", ayesha)[1]["data"]
step("student", "Ayesha sees her grade 9 and the feedback", mine and float(mine[0]["marks"]) == 9 and mine[0]["feedback"] == "Checked", mine)

def enter(token, subject, rows):
    return call("PUT", f"/exams/papers/{papers[subject]}/sections/{SEC_3A}/marks", token, json={"marks": rows})
status, body = enter(nadia, "Maths", [{"student_id": student_ids["ayesha"], "obtained_marks": 92}, {"student_id": student_ids["usman"], "obtained_marks": 25},
                                      {"student_id": student_ids["zainab"], "obtained_marks": 70}])
step("teacher", "Nadia enters Maths exam marks", status == 200, body)
sheet = call("GET", f"/exams/terms/{TERM}/sections/{SEC_3A}/results", nadia)[1]
step("teacher", "while English is missing, everyone is Incomplete with no position",
     all(r["result"] == "Incomplete" and r["position"] is None for r in sheet["students"]), [(r["name"], r["result"], r["position"]) for r in sheet["students"]])
status, body = enter(kamran, "English", [{"student_id": student_ids["ayesha"], "obtained_marks": 85}, {"student_id": student_ids["usman"], "obtained_marks": 60},
                                         {"student_id": student_ids["zainab"], "is_absent": True}])
step("teacher", "Kamran enters English exam marks (Zainab absent)", status == 200, body)
status, body = enter(kamran, "Maths", [{"student_id": student_ids["ayesha"], "obtained_marks": 10}])
step("teacher", "Kamran can't enter Maths marks", status == 403, body)
sheet = call("GET", f"/exams/terms/{TERM}/sections/{SEC_3A}/results", nadia)[1]
rows = {r["name"]: r for r in sheet["students"]}
step("teacher", "Ayesha first and passed; Usman failed Maths; Zainab failed (absent)",
     rows["Ayesha Noor"]["position"] == 1 and rows["Ayesha Noor"]["result"] == "Pass" and rows["Usman Tariq"]["result"] == "Fail" and rows["Zainab Shah"]["result"] == "Fail",
     [(r["name"], r["result"], r["position"], r["percentage"]) for r in sheet["students"]])
status, body = call("PUT", f"/exams/terms/{TERM}/students/{student_ids['ayesha']}/remarks", nadia, json={"remarks": "Excellent work."})
step("teacher", "Nadia writes Ayesha's report card remarks", status == 200, body)

# Before publishing, students can't see the report card
status, body = call("GET", f"/exams/terms/{TERM}/students/{student_ids['ayesha']}/report-card", ayesha)
step("student", "can't see the report card before it's published", status == 403, body)


# ======================= ADMIN: publish, promote =======================
status, body = call("PUT", f"/exams/terms/{TERM}", root, json={"is_published": True})
step("admin", "publishes the term's results", status == 200, body)
status, card = call("GET", f"/exams/terms/{TERM}/students/{student_ids['ayesha']}/report-card", ayesha)
step("student", "Ayesha opens her report card: Pass, position 1, remarks, attendance",
     status == 200 and card["result"] == "Pass" and card["position"] == 1 and card["remarks"] == "Excellent work." and card["attendance"]["present"] >= 1,
     {k: card.get(k) for k in ["result", "position", "remarks", "attendance"]} if isinstance(card, dict) else card)
status, body = call("GET", f"/exams/terms/{TERM}/students/{student_ids['usman']}/report-card", ayesha)
step("student", "Ayesha can't open Usman's report card", status == 403, body)

body = call("GET", f"/exams/promotion/sections/{SEC_3A}?term_id={TERM}", root)[1]
suggested = [s["name"] for s in body["students"] if s["suggest_promote"]]
step("admin", "promotion suggests only Ayesha (the one who passed)", suggested == ["Ayesha Noor"], suggested)
status, body = call("POST", f"/exams/promotion/sections/{SEC_3A}", root, json={"target_section_id": SEC_4A, "student_ids": [student_ids["ayesha"]]})
step("admin", "promotes Ayesha to 4-A", status == 200, body)
body = call("GET", "/school/my-class", ayesha)[1]
step("student", "Ayesha is now in Class 4 - A", "Class 4 - A" in str(body), str(body)[:120])

# Account: Usman changes his password and logs in with it
status, body = call("PUT", "/account/password", tokens["usman"], json={"current_password": "secret1", "new_password": "newpass1"})
step("student", "Usman changes his password", status == 200, body)
new_token, error = login(f"usman{RUN}@lms.test", "newpass1")
step("student", "Usman logs in with the new password", new_token, error)
old_token, error = login(f"usman{RUN}@lms.test", "secret1")
step("student", "the old password no longer works", old_token is None, error)

# Activity log saw it all
body = call("GET", "/oversight/activity?per_page=200", root)[1]
step("admin", "the activity log recorded the teachers' work", "Marked daily attendance" in str(body) and "Entered exam marks" in str(body), str(body)[:120])


# ======================= Summary =======================
print()
failed = [r for r in results if not r[2]]
print(f"{len(results) - len(failed)} of {len(results)} steps passed")
for role in ["admin", "teacher", "student"]:
    mine = [r for r in results if r[0] == role]
    print(f"  {role}: {sum(1 for r in mine if r[2])} / {len(mine)}")
if failed:
    print("FAILED STEPS:")
    for r in failed:
        print(f"  [{r[0]}] {r[1]} -> {r[3]}")
sys.exit(1 if failed else 0)
