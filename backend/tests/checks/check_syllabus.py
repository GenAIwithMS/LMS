"""Each section's syllabus is written by its subject teacher: chapters and daily topics, with
topics ticked off and assignments, class tests and diary entries made from them. The admin
and students can only see it. In-memory SQLite."""
import os, sys
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
from src.models import Admin, Teacher, Student, Assignment, ClassTest, SyllabusTopic

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
    db.session.add_all([make(Admin, "Principal", "root"), make(Teacher, "Sara", "sara"), make(Teacher, "Omar", "omar")])
    db.session.commit()
    SARA = Teacher.query.filter_by(username="sara").first().id
    OMAR = Teacher.query.filter_by(username="omar").first().id

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara"), "omar": login("omar")}

TODAY = pakistan_time().date()
CLASS_5 = client.get("/api/school/classes", headers=H["root"]).get_json()[4]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
B = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B", "incharge_id": OMAR}, headers=H["root"]).get_json()["section_id"]
MATHS = client.post(f"/api/school/classes/{CLASS_5}/subjects", json={"name": "Maths"}, headers=H["root"]).get_json()["subject_id"]
client.put(f"/api/school/sections/{A}/teachers", json={"subject_id": MATHS, "teacher_id": SARA}, headers=H["root"])
client.put(f"/api/school/sections/{B}/teachers", json={"subject_id": MATHS, "teacher_id": OMAR}, headers=H["root"])
for name, uname, section in [("Ali", "ali", A), ("Bilal", "bilal", B)]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1",
                                          "section_id": section, "roll_number": "1"}, headers=H["root"])
H["ali"] = login("ali"); H["bilal"] = login("bilal")

def syllabus(user, section=A):
    return client.get(f"/api/school/sections/{section}/subjects/{MATHS}/progress", headers=H[user]).get_json()

def add_chapter(user, title, section=A):
    return client.post(f"/api/school/sections/{section}/subjects/{MATHS}/chapters", json={"title": title}, headers=H[user])


print("--- Chapters: the section's subject teacher writes them")
r = add_chapter("sara", "Whole Numbers")
check("Sara adds a chapter to 5-A Maths", r.status_code == 201 and r.get_json()["chapter"]["number"] == 1, r.get_json())
CH1 = r.get_json()["chapter"]["id"]
CH2 = add_chapter("sara", "Fractions").get_json()["chapter"]["id"]
CH3 = add_chapter("sara", "Decimals").get_json()["chapter"]["id"]
check("the admin can't add chapters", add_chapter("root", "x").status_code == 403)
check("Omar (teaches Maths in 5-B, not 5-A) can't add to 5-A", add_chapter("omar", "x").status_code == 403)
check("a student can't add chapters", add_chapter("ali", "x").status_code == 403)
r = add_chapter("omar", "Shapes", section=B)
check("Omar writes 5-B's own syllabus", r.status_code == 201)
check("5-A and 5-B have different syllabuses",
      [c["title"] for c in syllabus("sara")["chapters"]] == ["Whole Numbers", "Fractions", "Decimals"] and [c["title"] for c in syllabus("omar", B)["chapters"]] == ["Shapes"])

r = client.put(f"/api/school/chapters/{CH2}", json={"title": "Fractions and Ratios"}, headers=H["sara"])
check("Sara renames a chapter", r.status_code == 200 and syllabus("sara")["chapters"][1]["title"] == "Fractions and Ratios")
check("Omar can't rename Sara's chapter", client.put(f"/api/school/chapters/{CH2}", json={"title": "x"}, headers=H["omar"]).status_code == 403)
r = client.put(f"/api/school/chapters/{CH3}/move", json={"direction": "up"}, headers=H["sara"])
check("moving Decimals up puts it second", r.status_code == 200 and [c["title"] for c in syllabus("sara")["chapters"]] == ["Whole Numbers", "Decimals", "Fractions and Ratios"])
check("the first chapter can't move up", client.put(f"/api/school/chapters/{CH1}/move", json={"direction": "up"}, headers=H["sara"]).status_code == 400)
check("numbers stay 1, 2, 3", [c["number"] for c in syllabus("sara")["chapters"]] == [1, 2, 3])


print("--- Daily topics")
def add_topic(chapter, title, planned=None, user="sara"):
    return client.post(f"/api/school/chapters/{chapter}/topics", json={"title": title, "planned_date": planned}, headers=H[user])
r = add_topic(CH1, "Place value", TODAY.isoformat())
check("Sara adds a topic with a planned day", r.status_code == 201 and r.get_json()["topic"]["planned_date"] == TODAY.isoformat(), r.get_json())
T1 = r.get_json()["topic"]["id"]
T2 = add_topic(CH1, "Comparing numbers").get_json()["topic"]["id"]
T3 = add_topic(CH1, "Rounding").get_json()["topic"]["id"]
check("Omar can't add a topic to Sara's chapter", add_topic(CH1, "x", user="omar").status_code == 403)
client.put(f"/api/school/topics/{T3}/move", json={"direction": "up"}, headers=H["sara"])
check("topics can be reordered", [t["title"] for t in syllabus("sara")["chapters"][0]["topics"]] == ["Place value", "Rounding", "Comparing numbers"])
r = client.put(f"/api/school/topics/{T2}", json={"title": "Comparing and ordering", "planned_date": (TODAY + timedelta(days=2)).isoformat()}, headers=H["sara"])
check("a topic can be renamed and given another day", r.status_code == 200 and r.get_json()["topic"]["title"] == "Comparing and ordering")


print("--- Ticking topics off moves the chapter's progress")
def chapter_status(number=0):
    return syllabus("sara")["chapters"][number]["status"]
r = client.put(f"/api/school/topics/{T1}/done", json={"done": True}, headers=H["sara"])
check("ticking a topic off records the day", r.status_code == 200 and r.get_json()["topic"]["is_done"] and r.get_json()["topic"]["done_on"] == TODAY.isoformat(), r.get_json())
check("one of three topics done: the chapter is in progress", chapter_status() == "in_progress", chapter_status())
client.put(f"/api/school/topics/{T2}/done", json={"done": True}, headers=H["sara"])
client.put(f"/api/school/topics/{T3}/done", json={"done": True}, headers=H["sara"])
check("all topics done: the chapter is done", chapter_status() == "done")
client.put(f"/api/school/topics/{T3}/done", json={"done": False}, headers=H["sara"])
check("un-ticking one: back to in progress", chapter_status() == "in_progress")
check("the admin can't tick topics", client.put(f"/api/school/topics/{T3}/done", json={"done": True}, headers=H["root"]).status_code == 403)
r = client.put(f"/api/school/sections/{A}/chapters/{CH1}/progress", json={"status": "done"}, headers=H["sara"])
check("a chapter with topics can't be set by hand", r.status_code == 400 and "topics" in r.get_json()["message"], r.get_json())
r = client.put(f"/api/school/sections/{A}/chapters/{CH3}/progress", json={"status": "done"}, headers=H["sara"])
check("a chapter without topics still can", r.status_code == 200)
data = syllabus("sara")
check("the summary counts topics", data["topic_count"] == 3 and data["topics_done"] == 2, (data["topic_count"], data["topics_done"]))


print("--- Making an assignment, a class test and a diary entry from a topic")
due = (TODAY + timedelta(days=5)).isoformat()
r = client.post("/api/create/assignments", json={"title": "Place value homework", "description": "x", "subject_id": MATHS, "section_id": A,
                                                "due_date": due, "total_marks": 10, "topic_id": T1}, headers=H["sara"])
check("an assignment set on a topic", r.status_code == 201, r.get_json())
r = client.post("/api/school/class-tests", json={"section_id": A, "subject_id": MATHS, "title": "Place value quiz", "date": TODAY.isoformat(),
                                                "total_marks": 10, "topic_id": T1}, headers=H["sara"])
check("a class test on a topic takes the topic's chapter", r.status_code == 201 and r.get_json()["test"]["chapter_id"] == CH1 and r.get_json()["test"]["topic_title"] == "Place value", r.get_json())
TEST = r.get_json()["test"]["id"]
r = client.post(f"/api/school/sections/{A}/diary", json={"subject_id": MATHS, "date": TODAY.isoformat(), "classwork": "Place value", "topic_id": T1}, headers=H["sara"])
check("a diary entry written from a topic", r.status_code in (200, 201) and r.get_json()["entry"]["topic_title"] == "Place value", r.get_json())
links = syllabus("sara")["chapters"][0]["topics"][0]["links"]
check("the topic lists what was made from it",
      [a["title"] for a in links["assignments"]] == ["Place value homework"] and [t["title"] for t in links["class_tests"]] == ["Place value quiz"] and len(links["diary"]) == 1, links)
omar_topic = add_topic(client.post(f"/api/school/sections/{B}/subjects/{MATHS}/chapters", json={"title": "B chapter"}, headers=H["omar"]).get_json()["chapter"]["id"],
                       "B topic", user="omar").get_json()["topic"]["id"]
r = client.post("/api/create/assignments", json={"title": "Wrong", "description": "x", "subject_id": MATHS, "section_id": A,
                                                "due_date": due, "total_marks": 10, "topic_id": omar_topic}, headers=H["sara"])
check("another section's topic can't be used", r.status_code == 400, r.get_json())
listed = client.get("/api/get/assignments", headers=H["ali"]).get_json()["assignments"]
check("students see which topic an assignment is on", [a["topic_title"] for a in listed if a["title"] == "Place value homework"] == ["Place value"], listed)


print("--- Who can see it")
check("Sara can edit 5-A Maths", syllabus("sara")["can_edit"] is True)
check("the admin sees it, read-only", syllabus("root")["can_edit"] is False and len(syllabus("root")["chapters"]) == 3)
check("Ali (5-A) sees it, read-only", syllabus("ali")["can_edit"] is False and syllabus("ali")["chapters"][0]["topics"][0]["is_done"] is True)
check("Bilal (5-B) can't see 5-A's", client.get(f"/api/school/sections/{A}/subjects/{MATHS}/progress", headers=H["bilal"]).status_code == 403)
chapters = client.get(f"/api/school/sections/{A}/subjects/{MATHS}/chapters", headers=H["sara"]).get_json()["data"]
check("the chapter picker lists 5-A's chapters with topics", [c["title"] for c in chapters] == ["Whole Numbers", "Decimals", "Fractions and Ratios"] and len(chapters[0]["topics"]) == 3)
section_view = client.get(f"/api/school/sections/{A}/progress", headers=H["root"]).get_json()["subjects"][0]
check("the section summary counts 5-A's own chapters", section_view["chapter_count"] == 3 and section_view["done_count"] == 1, section_view)
coverage = client.get("/api/oversight/dashboard", headers=H["root"]).get_json()["syllabus_coverage"][0]["sections"]
check("oversight shows each section's own coverage", [(s["section_name"], s["subjects"][0]["chapter_count"]) for s in coverage] == [("Class 5 - A", 3), ("Class 5 - B", 2)], coverage)


print("--- Deleting")
r = client.delete(f"/api/school/topics/{T1}", headers=H["sara"])
check("Sara deletes a topic", r.status_code == 200)
with app.app_context():
    homework = Assignment.query.filter_by(title="Place value homework").first()
    check("its assignment stays, without the topic", homework is not None and homework.topic_id is None)
check("the other topics move up", [(t["number"], t["title"]) for t in syllabus("sara")["chapters"][0]["topics"]] == [(1, "Rounding"), (2, "Comparing and ordering")])
r = client.delete(f"/api/school/chapters/{CH1}", headers=H["sara"])
check("Sara deletes a chapter", r.status_code == 200)
with app.app_context():
    test = ClassTest.query.get(TEST)
    check("its class test stays, without the chapter", test is not None and test.chapter_id is None)
    check("its topics are gone", SyllabusTopic.query.filter_by(chapter_id=CH1).count() == 0)
check("the other chapters move up", [(c["number"], c["title"]) for c in syllabus("sara")["chapters"]] == [(1, "Decimals"), (2, "Fractions and Ratios")])
check("the admin can't delete chapters", client.delete(f"/api/school/chapters/{CH2}", headers=H["root"]).status_code == 403)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
