"""Exams (Phase 3): terms, papers, question paper review, marks entry and locking, report cards
with positions, publishing, analysis, and promotion. In-memory SQLite."""
import os, sys, io, shutil, tempfile
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from datetime import timedelta
from src import create_app
from src.db import db, pakistan_time
from src.models import Admin, Teacher, Student
import src.services.exam as exam_service

# Question papers go to a temporary folder, not the real uploads folder
TEMP_FOLDER = tempfile.mkdtemp()
exam_service.QUESTION_PAPER_FOLDER = TEMP_FOLDER

app = create_app()
client = app.test_client()
fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond:
        fails.append(name)

def make(cls, name, uname, **kw):
    u = cls(name=name, username=uname, email=f"{uname}@x.com", **kw); u.set_password("secret1"); return u

with app.app_context():
    db.create_all()
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara"), make(Teacher, "Omar", "omar"), make(Teacher, "Zara", "zara")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id
    OMAR = Teacher.query.filter_by(username="omar").first().id
    ZARA = Teacher.query.filter_by(username="zara").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara"), "omar": login("omar"), "zara": login("zara")}

TODAY = pakistan_time().date()
def day(offset):
    return (TODAY + timedelta(days=offset)).isoformat()

# School: Class 5 with 5-A (incharge Sara) and 5-B (incharge Omar), Class 6 with 6-A.
# 5-A: Sara teaches Maths, Omar Science, Zara English. 5-B: Omar teaches Maths.
classes = client.get("/api/school/classes", headers=H["root"]).get_json()
CLASS_5 = classes[4]["id"]; CLASS_6 = classes[5]["id"]; CLASS_7 = classes[6]["id"]
SESSION = client.post("/api/school/sessions", json={"name": "2026-27", "start_date": day(-200), "end_date": day(160)}, headers=H["root"]).get_json()["session_id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
B = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B", "incharge_id": OMAR}, headers=H["root"]).get_json()["section_id"]
SIX_A = client.post(f"/api/school/classes/{CLASS_6}/sections", json={"name": "A"}, headers=H["root"]).get_json()["section_id"]
SEVEN_A = client.post(f"/api/school/classes/{CLASS_7}/sections", json={"name": "A"}, headers=H["root"]).get_json()["section_id"]
S = {}
for name in ["Maths", "Science", "English"]:
    S[name] = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": name}, headers=H["root"]).get_json()["subject_id"]
for subject, teacher in [("Maths", SARA), ("Science", OMAR), ("English", ZARA)]:
    client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": S[subject], "teacher_id": teacher}, headers=H["root"])
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": S["Maths"], "teacher_id": OMAR}, headers=H["root"])
for name, uname, section, roll in [("Ali", "ali", A, "1"), ("Hina", "hina", A, "2"), ("Usman", "usman", A, "3"), ("Bilal", "bilal", B, "1")]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1",
                                          "section_id": section, "roll_number": roll}, headers=H["root"])
with app.app_context():
    ST = {}
    for uname in ["ali", "hina", "usman", "bilal"]:
        ST[uname] = Student.query.filter_by(username=uname).first().id
H["ali"] = login("ali")

print("--- Terms")
term = {"session_id": SESSION, "name": "First Term", "start_date": day(-14), "end_date": day(-1)}
r = client.post("/api/exams/terms", json=term, headers=H["root"])
check("admin adds First Term", r.status_code == 201, r.get_json())
TERM = r.get_json()["term"]["id"]
check("the same term name can't be added twice", client.post("/api/exams/terms", json=term, headers=H["root"]).status_code == 409)
r = client.post("/api/exams/terms", json=dict(term, name="Mid Term", start_date=day(5), end_date=day(1)), headers=H["root"])
check("a term must end after it starts", r.status_code == 400, r.get_json())
check("a teacher can't add a term", client.post("/api/exams/terms", json=dict(term, name="X Term"), headers=H["sara"]).status_code == 403)
check("a student sees no terms before results are published", client.get("/api/exams/terms", headers=H["ali"]).get_json() == [])

print("--- Papers")
r = client.post(f"/api/exams/terms/{TERM}/papers", json={"class_id": CLASS_5}, headers=H["root"])
check("admin sets up Class 5's papers (one per subject)", r.status_code == 201 and r.get_json()["added"] == 3, r.get_json())
r = client.post(f"/api/exams/terms/{TERM}/papers", json={"class_id": CLASS_5}, headers=H["root"])
check("setting up again adds nothing", r.get_json()["added"] == 0)
papers = client.get(f"/api/exams/terms/{TERM}/papers", headers=H["root"]).get_json()
P = {paper["subject_name"]: paper["id"] for paper in papers}
check("papers default to 100 total and 33 to pass", papers[0]["total_marks"] == "100" and papers[0]["passing_marks"] == "33", papers[0])
r = client.put(f"/api/exams/papers/{P['English']}", json={"total_marks": 50, "passing_marks": 60}, headers=H["root"])
check("passing marks can't be more than the total", r.status_code == 400)
r = client.put(f"/api/exams/papers/{P['English']}", json={"total_marks": 50, "passing_marks": 17, "exam_date": day(-3)}, headers=H["root"])
check("admin changes English to 50 marks", r.status_code == 200)
check("teachers can't change papers", client.put(f"/api/exams/papers/{P['Maths']}", json={"total_marks": 10}, headers=H["sara"]).status_code == 403)
sara_papers = client.get(f"/api/exams/terms/{TERM}/my-papers", headers=H["sara"]).get_json()["papers"]
omar_papers = client.get(f"/api/exams/terms/{TERM}/my-papers", headers=H["omar"]).get_json()["papers"]
check("Sara marks Maths in 5-A only", [(p["subject_name"], p["section_name"]) for p in sara_papers] == [("Maths", "Class 5 - A")], sara_papers)
check("Omar marks Science in 5-A and Maths in 5-B",
      sorted((p["subject_name"], p["section_name"]) for p in omar_papers) == [("Maths", "Class 5 - B"), ("Science", "Class 5 - A")], omar_papers)

print("--- Question papers")
def upload(user, content, filename="maths.pdf", paper="Maths"):
    return client.post(f"/api/exams/papers/{P[paper]}/question-paper", data={"file": (io.BytesIO(content), filename)},
                       headers=H[user], content_type="multipart/form-data")
PDF = b"%PDF-1.4 a small test paper"
check("a Word file is refused", upload("sara", b"hello", "maths.docx").status_code == 400)
check("a file renamed to .pdf is refused", upload("sara", b"MZ fake", "maths.pdf").status_code == 400)
check("Zara doesn't teach Maths, so she can't upload it", upload("zara", PDF).status_code == 403)
r = upload("sara", PDF)
check("Sara uploads the Maths question paper", r.status_code == 200, r.get_json())
check("a student can't download a question paper", client.get(f"/api/exams/papers/{P['Maths']}/question-paper", headers=H["ali"]).status_code == 403)
r = client.get(f"/api/exams/papers/{P['Maths']}/question-paper", headers=H["root"])
check("the admin downloads it", r.status_code == 200 and r.data == PDF and "maths.pdf" in r.headers.get("Content-Disposition", ""))
check("returning it needs a note", client.put(f"/api/exams/papers/{P['Maths']}/review", json={"approve": False}, headers=H["root"]).status_code == 400)
client.put(f"/api/exams/papers/{P['Maths']}/review", json={"approve": False, "note": "Add a diagram question"}, headers=H["root"])
paper = [p for p in client.get(f"/api/exams/terms/{TERM}/my-papers", headers=H["sara"]).get_json()["papers"] if p["subject_name"] == "Maths"][0]
check("Sara sees it was returned with the note", paper["question_status"] == "returned" and paper["review_note"] == "Add a diagram question", paper)
upload("sara", PDF + b" v2")
r = client.put(f"/api/exams/papers/{P['Maths']}/review", json={"approve": True}, headers=H["root"])
check("the admin approves the new version", r.status_code == 200)
check("an approved paper can't be replaced", upload("sara", PDF).status_code == 409)
check("only one file is kept on disk", len(os.listdir(TEMP_FOLDER)) == 1, os.listdir(TEMP_FOLDER))

print("--- Marks entry")
def enter(user, subject, rows, section=A):
    return client.put(f"/api/exams/papers/{P[subject]}/sections/{section}/marks", json={"marks": rows}, headers=H[user])
r = enter("sara", "Maths", [{"student_id": ST["ali"], "obtained_marks": 85}, {"student_id": ST["hina"], "obtained_marks": 40},
                            {"student_id": ST["usman"], "is_absent": True}])
check("Sara enters 5-A Maths (Usman absent)", r.status_code == 200, r.get_json())
check("marks can't be over the total", enter("sara", "Maths", [{"student_id": ST["ali"], "obtained_marks": 101}]).status_code == 400)
check("a 5-B student can't be marked on the 5-A sheet", enter("sara", "Maths", [{"student_id": ST["bilal"], "obtained_marks": 50}]).status_code == 400)
check("Omar can't enter 5-A Maths", enter("omar", "Maths", [{"student_id": ST["ali"], "obtained_marks": 10}]).status_code == 403)
check("the admin doesn't enter marks", enter("root", "Maths", [{"student_id": ST["ali"], "obtained_marks": 10}]).status_code == 403)
enter("omar", "Science", [{"student_id": ST["ali"], "obtained_marks": 70}, {"student_id": ST["hina"], "obtained_marks": 25}, {"student_id": ST["usman"], "obtained_marks": 60}])
enter("zara", "English", [{"student_id": ST["ali"], "obtained_marks": 45}, {"student_id": ST["hina"], "obtained_marks": 50}, {"student_id": ST["usman"], "obtained_marks": 33}])
check("English is out of 50 now", enter("zara", "English", [{"student_id": ST["hina"], "obtained_marks": 51}]).status_code == 400)
enter("zara", "English", [{"student_id": ST["hina"], "obtained_marks": 20}])
sheet = client.get(f"/api/exams/papers/{P['Maths']}/sections/{A}/marks", headers=H["sara"]).get_json()
check("the marks sheet shows marks and absences",
      [(s["name"], s["obtained_marks"], s["is_absent"]) for s in sheet["students"]] == [("Ali", "85", False), ("Hina", "40", False), ("Usman", None, True)], sheet["students"])
check("the class incharge can view another subject's sheet", client.get(f"/api/exams/papers/{P['Science']}/sections/{A}/marks", headers=H["sara"]).status_code == 200)
check("Zara can't view the Maths sheet", client.get(f"/api/exams/papers/{P['Maths']}/sections/{A}/marks", headers=H["zara"]).status_code == 403)

print("--- Result sheet and positions")
# Totals out of 250: Ali 85+70+45 = 200, Hina 40+25+20 = 85, Usman 0(absent)+60+33 = 93
result = client.get(f"/api/exams/terms/{TERM}/sections/{A}/results", headers=H["root"]).get_json()
rows = {s["name"]: s for s in result["students"]}
check("Ali: 200/250 = 80%, A+, first, passed",
      rows["Ali"]["total_obtained"] == "200" and rows["Ali"]["percentage"] == 80.0 and rows["Ali"]["grade"] == "A+" and rows["Ali"]["position"] == 1 and rows["Ali"]["result"] == "Pass", rows["Ali"])
check("Usman: second, but failed (absent in Maths)", rows["Usman"]["position"] == 2 and rows["Usman"]["result"] == "Fail", rows["Usman"])
check("Hina: third, failed Science (25 < 33)", rows["Hina"]["position"] == 3 and rows["Hina"]["result"] == "Fail", rows["Hina"])
check("1 of 3 passed", result["passed_count"] == 1)
enter("zara", "English", [{"student_id": ST["hina"], "obtained_marks": 28}])   # Hina now 93, same as Usman
rows = {s["name"]: s for s in client.get(f"/api/exams/terms/{TERM}/sections/{A}/results", headers=H["root"]).get_json()["students"]}
check("equal totals share a position (1, 2, 2)", (rows["Ali"]["position"], rows["Hina"]["position"], rows["Usman"]["position"]) == (1, 2, 2), [(n, r["position"]) for n, r in rows.items()])
check("Zara (teaches in 5-A) can see the result sheet", client.get(f"/api/exams/terms/{TERM}/sections/{A}/results", headers=H["zara"]).status_code == 200)
check("Zara can't see 5-B's result sheet", client.get(f"/api/exams/terms/{TERM}/sections/{B}/results", headers=H["zara"]).status_code == 403)
result_b = client.get(f"/api/exams/terms/{TERM}/sections/{B}/results", headers=H["root"]).get_json()
check("5-B's sheet: Bilal has no marks yet, so his result is incomplete", result_b["students"][0]["result"] == "Incomplete" and result_b["students"][0]["position"] is None, result_b["students"])

print("--- Report card, remarks and publishing")
client.post(f"/api/school/sections/{A}/attendance", json={"date": day(-2), "records": [{"student_id": ST["ali"], "status": "present"}]}, headers=H["sara"])
client.post(f"/api/school/sections/{A}/attendance", json={"date": day(-1), "records": [{"student_id": ST["ali"], "status": "absent"}]}, headers=H["sara"])
client.post(f"/api/school/sections/{A}/attendance", json={"date": day(0), "records": [{"student_id": ST["ali"], "status": "absent"}]}, headers=H["sara"])
r = client.put(f"/api/exams/terms/{TERM}/students/{ST['ali']}/remarks", json={"remarks": "Hard working. Keep it up."}, headers=H["sara"])
check("Sara (incharge) writes Ali's remarks", r.status_code == 200, r.get_json())
check("Omar (not the incharge) can't", client.put(f"/api/exams/terms/{TERM}/students/{ST['ali']}/remarks", json={"remarks": "x"}, headers=H["omar"]).status_code == 403)
check("Ali can't see his card before it's published", client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["ali"]).status_code == 403)
card = client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["sara"]).get_json()
check("the report card has subjects, position, strength, remarks",
      len(card["subjects"]) == 3 and card["position"] == 1 and card["class_strength"] == 3 and card["remarks"] == "Hard working. Keep it up." and card["section_name"] == "Class 5 - A", card)
check("attendance counts only the term's days (today is after the term)",
      card["attendance"]["present"] == 1 and card["attendance"]["absent"] == 1 and card["attendance"]["percentage"] == 50.0, card["attendance"])
maths = [s for s in card["subjects"] if s["subject_name"] == "Maths"][0]
check("each subject has marks, percentage and grade", maths["obtained_marks"] == "85" and maths["percentage"] == 85.0 and maths["grade"] == "A+" and maths["passed"], maths)
r = client.put(f"/api/exams/terms/{TERM}", json={"is_published": True}, headers=H["root"])
check("admin publishes the term", r.status_code == 200 and r.get_json()["term"]["is_published"])
check("Ali now sees the term", [t["name"] for t in client.get("/api/exams/terms", headers=H["ali"]).get_json()] == ["First Term"])
check("Ali opens his own report card", client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["ali"]).status_code == 200)
check("Ali can't open Hina's", client.get(f"/api/exams/terms/{TERM}/students/{ST['hina']}/report-card", headers=H["ali"]).status_code == 403)
check("remarks can't change after publishing", client.put(f"/api/exams/terms/{TERM}/students/{ST['ali']}/remarks", json={"remarks": "x"}, headers=H["sara"]).status_code == 403)

print("--- Locking")
client.put(f"/api/exams/terms/{TERM}", json={"is_locked": True}, headers=H["root"])
check("after the admin locks the term, marks can't change", enter("sara", "Maths", [{"student_id": ST["ali"], "obtained_marks": 90}]).status_code == 403)
client.put(f"/api/exams/terms/{TERM}", json={"is_locked": False, "marks_deadline": day(-1)}, headers=H["root"])
check("after the deadline, marks can't change either", enter("sara", "Maths", [{"student_id": ST["ali"], "obtained_marks": 90}]).status_code == 403)
term_info = client.get(f"/api/exams/terms/{TERM}", headers=H["root"]).get_json()
check("the term shows as closed", term_info["is_closed"] and not term_info["is_locked"], term_info)
client.put(f"/api/exams/terms/{TERM}", json={"marks_deadline": None}, headers=H["root"])
check("removing the deadline opens it again", enter("sara", "Maths", [{"student_id": ST["ali"], "obtained_marks": 85}]).status_code == 200)

print("--- Analysis")
analysis = client.get(f"/api/exams/terms/{TERM}/analysis", headers=H["root"]).get_json()
section_a = [s for s in analysis["sections"] if s["section_name"] == "Class 5 - A"][0]
maths_row = [s for s in section_a["subjects"] if s["subject_name"] == "Maths"][0]
check("5-A Maths: average 41.7% (absent counts as 0), 66.7% passed, highest 85, Sara",
      maths_row["average_percentage"] == 41.7 and maths_row["pass_percentage"] == 66.7 and maths_row["highest_marks"] == "85" and maths_row["teacher_name"] == "Sara", maths_row)
check("top students start with Ali", section_a["top_students"][0]["name"] == "Ali", section_a["top_students"])
check("each teacher's subjects are listed", sorted(t["teacher_name"] for t in analysis["teachers"]) == ["Omar", "Sara", "Zara"], analysis["teachers"])
check("teachers can't open the analysis", client.get(f"/api/exams/terms/{TERM}/analysis", headers=H["sara"]).status_code == 403)

print("--- Promotion")
promo = client.get(f"/api/exams/promotion/sections/{A}?term_id={TERM}", headers=H["root"]).get_json()
suggest = {s["name"]: s["suggest_promote"] for s in promo["students"]}
check("the list suggests promoting those who passed", suggest == {"Ali": True, "Hina": False, "Usman": False}, suggest)
check("next class is Class 6 with its sections", promo["next_class_name"] == "Class 6" and [t["full_name"] for t in promo["target_sections"]] == ["Class 6 - A"], promo)
r = client.post(f"/api/exams/promotion/sections/{A}", json={"target_section_id": SEVEN_A, "student_ids": [ST["ali"]]}, headers=H["root"])
check("students can't skip a class", r.status_code == 400)
r = client.post(f"/api/exams/promotion/sections/{A}", json={"target_section_id": SIX_A, "student_ids": [ST["bilal"]]}, headers=H["root"])
check("only students of this section can be promoted", r.status_code == 400)
check("teachers can't promote", client.post(f"/api/exams/promotion/sections/{A}", json={"target_section_id": SIX_A, "student_ids": [ST["ali"]]}, headers=H["sara"]).status_code == 403)
r = client.post(f"/api/exams/promotion/sections/{A}", json={"target_section_id": SIX_A, "student_ids": [ST["ali"]]}, headers=H["root"])
check("admin promotes Ali to 6-A", r.status_code == 200, r.get_json())
with app.app_context():
    check("Ali is now in 6-A", Student.query.get(ST["ali"]).section_id == SIX_A)
card = client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["root"]).get_json()
check("Ali's old report card still says Class 5 - A, first of 3", card["section_name"] == "Class 5 - A" and card["position"] == 1 and card["class_strength"] == 3, card)
check("Sara (5-A incharge) can still open it", client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["sara"]).status_code == 200)

print("--- Grading scale (editable by the admin)")
scale = client.get("/api/exams/grading-scale", headers=H["sara"]).get_json()
check("the default scale is A+ 80, A 70, B 60, C 50, D 40, E 33, F 0",
      [(b["grade"], b["min_percentage"]) for b in scale] == [("A+", 80), ("A", 70), ("B", 60), ("C", 50), ("D", 40), ("E", 33), ("F", 0)], scale)
custom = [{"grade": "A1", "min_percentage": 90}, {"grade": "A", "min_percentage": 80}, {"grade": "B", "min_percentage": 65},
          {"grade": "C", "min_percentage": 50}, {"grade": "Fail", "min_percentage": 0}]
check("teachers can't change the scale", client.put("/api/exams/grading-scale", json={"bands": custom}, headers=H["sara"]).status_code == 403)
r = client.put("/api/exams/grading-scale", json={"bands": custom[:-1]}, headers=H["root"])
check("the lowest grade must start at 0%", r.status_code == 400 and "0%" in r.get_json()["message"], r.get_json())
r = client.put("/api/exams/grading-scale", json={"bands": custom + [{"grade": "a1", "min_percentage": 95}]}, headers=H["root"])
check("the same grade can't be listed twice", r.status_code == 400, r.get_json())
r = client.put("/api/exams/grading-scale", json={"bands": custom + [{"grade": "X", "min_percentage": 90}]}, headers=H["root"])
check("two grades can't start at the same percentage", r.status_code == 400, r.get_json())
check("percentages must be 0 to 100", client.put("/api/exams/grading-scale", json={"bands": [{"grade": "A", "min_percentage": 120}, {"grade": "F", "min_percentage": 0}]}, headers=H["root"]).status_code == 400)
r = client.put("/api/exams/grading-scale", json={"bands": custom}, headers=H["root"])
check("the admin saves the school's own scale", r.status_code == 200, r.get_json())
card = client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["root"]).get_json()
maths = [s for s in card["subjects"] if s["subject_name"] == "Maths"][0]
check("report cards use it: Ali's 80% is now A, Maths 85% is A",
      card["grade"] == "A" and maths["grade"] == "A" and [b["grade"] for b in card["grade_scale"]] == ["A1", "A", "B", "C", "Fail"], (card["grade"], maths["grade"]))
hina_sheet = [s for s in client.get(f"/api/exams/terms/{TERM}/sections/{A}/results", headers=H["root"]).get_json()["students"] if s["name"] == "Hina"][0]
check("and the result sheet too (Hina 37.2% = Fail)", hina_sheet["grade"] == "Fail", hina_sheet["grade"])
r = client.post("/api/exams/grading-scale/reset", headers=H["root"])
check("reset brings back the default scale", r.status_code == 200 and r.get_json()["scale"][0] == {"grade": "A+", "min_percentage": 80.0}, r.get_json())
card = client.get(f"/api/exams/terms/{TERM}/students/{ST['ali']}/report-card", headers=H["root"]).get_json()
check("Ali is A+ again", card["grade"] == "A+", card["grade"])

print("--- Safe deletes")
check("a term with marks can't be deleted", client.delete(f"/api/exams/terms/{TERM}", headers=H["root"]).status_code == 409)
check("a paper with marks can't be deleted", client.delete(f"/api/exams/papers/{P['Maths']}", headers=H["root"]).status_code == 409)
check("a subject with exam papers can't be deleted", client.delete(f"/api/school/subjects/{S['English']}", headers=H["root"]).status_code == 409)
empty = client.post("/api/exams/terms", json=dict(term, name="Mid Term"), headers=H["root"]).get_json()["term"]["id"]
client.post(f"/api/exams/terms/{empty}/papers", json={"class_id": CLASS_5}, headers=H["root"])
check("an unused term (with papers) can be deleted", client.delete(f"/api/exams/terms/{empty}", headers=H["root"]).status_code == 200)

shutil.rmtree(TEMP_FOLDER)
print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
