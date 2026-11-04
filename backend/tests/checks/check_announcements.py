"""Announcements: the admin posts to everyone, teachers or students, for the whole school,
a class or a section; teachers post for their sections; everyone sees only what is meant
for them. In-memory SQLite."""
import os, sys
os.environ.update(RATELIMIT_ENABLED="false", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from src import create_app
from src.db import db
from src.models import Admin, Teacher

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

def login(user):
    token = client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
H = {"root": login("root"), "sara": login("sara"), "omar": login("omar"), "zara": login("zara")}

# Class 5: 5-A (incharge Sara), 5-B (incharge Omar). Class 6: 6-A (no teachers). Zara teaches nowhere.
classes = client.get("/api/school/classes", headers=H["root"]).get_json()
CLASS_5 = classes[4]["id"]; CLASS_6 = classes[5]["id"]
A = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "A", "incharge_id": SARA}, headers=H["root"]).get_json()["section_id"]
B = client.post(f"/api/school/classes/{CLASS_5}/sections", json={"name": "B", "incharge_id": OMAR}, headers=H["root"]).get_json()["section_id"]
SIX_A = client.post(f"/api/school/classes/{CLASS_6}/sections", json={"name": "A"}, headers=H["root"]).get_json()["section_id"]
for name, uname, section in [("Ali", "ali", A), ("Bilal", "bilal", B), ("Kamal", "kamal", SIX_A)]:
    client.post("/api/add/student", json={"name": name, "username": uname, "email": f"{uname}@x.com", "password": "secret1", "section_id": section}, headers=H["root"])
for uname in ["ali", "bilal", "kamal"]:
    H[uname] = login(uname)

def post(title, audience="all", class_id=None, section_id=None, user="root"):
    return client.post("/api/admin/announcements", json={"title": title, "content": f"About {title}", "target_audience": audience,
                                                         "class_id": class_id, "section_id": section_id}, headers=H[user])

def titles(user):
    return sorted(a["title"] for a in client.get("/api/get/announcements", headers=H[user]).get_json())

print("--- The admin posts")
r = post("Holiday on Friday")
check("the admin posts to the whole school", r.status_code == 201, r.get_json())
data = r.get_json()["announcement"]
check("it shows the admin as the author and where it goes",
      data["author_role"] == "admin" and data["author_name"] == "Principal" and data["where"] == "Whole school" and data["audience_text"] == "Everyone", data)
check("staff meeting for teachers only", post("Staff meeting", "teachers").status_code == 201)
check("fee notice for students only", post("Fee reminder", "students").status_code == 201)
r = post("Class 5 picnic", "all", class_id=CLASS_5)
check("for one class (all its sections)", r.status_code == 201 and r.get_json()["announcement"]["where"] == "Class 5 (all sections)", r.get_json())
r = post("5-B test on Monday", "students", class_id=CLASS_5, section_id=B)
check("for one section", r.status_code == 201 and r.get_json()["announcement"]["where"] == "Class 5 - B", r.get_json())
check("a section of another class is refused", post("Wrong", class_id=CLASS_6, section_id=A).status_code == 400)
check("an unknown class is refused", post("Wrong 2", class_id=99999).status_code == 400)
check("the same title twice is refused", post("Holiday on Friday").status_code == 400)
check("an unknown audience is refused", post("Odd", "parents").status_code == 400)
check("an empty message is refused", client.post("/api/admin/announcements", json={"title": "Empty", "content": ""}, headers=H["root"]).status_code == 400)
check("teachers can't post as the admin", post("Not mine", user="sara").status_code == 403)
check("students can't either", post("Not mine", user="ali").status_code == 403)

print("--- Teachers post for their sections")
r = client.post("/api/create/announcement", json={"title": "5-A homework", "content": "Read ch 2", "target_audience": "students", "section_id": A}, headers=H["sara"])
check("Sara posts for her students in 5-A", r.status_code == 201, r.get_json())
r = client.post("/api/create/announcement", json={"title": "5-B duty", "content": "Gate duty", "target_audience": "teachers", "section_id": B}, headers=H["omar"])
check("Omar posts for teachers of 5-B", r.status_code == 201)
r = client.post("/api/create/announcement", json={"title": "Bad", "content": "x", "target_audience": "everybody", "section_id": A}, headers=H["sara"])
check("a teacher's audience must be all, teachers or students", r.status_code == 400)

print("--- Everyone sees only what is meant for them")
check("the admin sees everything", titles("root") == sorted(["Holiday on Friday", "Staff meeting", "Fee reminder", "Class 5 picnic", "5-B test on Monday", "5-A homework", "5-B duty"]), titles("root"))
check("Ali (5-A): school-wide for all/students, Class 5, and his section's homework",
      titles("ali") == sorted(["Holiday on Friday", "Fee reminder", "Class 5 picnic", "5-A homework"]), titles("ali"))
check("Bilal (5-B): also the 5-B test, not 5-A's homework",
      titles("bilal") == sorted(["Holiday on Friday", "Fee reminder", "Class 5 picnic", "5-B test on Monday"]), titles("bilal"))
check("Kamal (6-A): only the school-wide ones", titles("kamal") == sorted(["Holiday on Friday", "Fee reminder"]), titles("kamal"))
check("Sara: school-wide for all/teachers, Class 5, and her own; not students-only ones or 5-B's duty",
      titles("sara") == sorted(["Holiday on Friday", "Staff meeting", "Class 5 picnic", "5-A homework"]), titles("sara"))
check("Omar: also his own 5-B duty", titles("omar") == sorted(["Holiday on Friday", "Staff meeting", "Class 5 picnic", "5-B duty"]), titles("omar"))
check("Zara (no classes): only the school-wide ones for teachers", titles("zara") == sorted(["Holiday on Friday", "Staff meeting"]), titles("zara"))
r = client.get("/api/get/announcements?title=Fee reminder", headers=H["sara"])
check("a teacher can't open a students-only announcement by title", r.status_code == 404)
r = client.get("/api/get/announcements?title=Staff meeting", headers=H["ali"])
check("a student can't open a teachers-only one", r.status_code == 404)

print("--- Changing and deleting")
all_rows = client.get("/api/get/announcements", headers=H["root"]).get_json()
ID = {a["title"]: a["id"] for a in all_rows}
r = client.put(f"/api/admin/announcements/{ID['Holiday on Friday']}", json={"title": "Holiday on Saturday", "content": "Moved", "target_audience": "students"}, headers=H["root"])
check("the admin edits their announcement", r.status_code == 200 and r.get_json()["announcement"]["title"] == "Holiday on Saturday", r.get_json())
check("now teachers don't see it (students only)", "Holiday on Saturday" not in titles("sara") and "Holiday on Saturday" in titles("ali"))
r = client.put(f"/api/admin/announcements/{ID['Class 5 picnic']}", json={"class_id": None, "section_id": None}, headers=H["root"])
check("moving it to the whole school", r.status_code == 200 and "Class 5 picnic" in titles("kamal"))
check("the admin can't edit a teacher's announcement here", client.put(f"/api/admin/announcements/{ID['5-A homework']}", json={"content": "x"}, headers=H["root"]).status_code == 404)
check("teachers can't edit the admin's announcement", client.put("/api/update/announcement?title=Staff meeting", json={"content": "x"}, headers=H["sara"]).status_code == 403)
check("teachers can't delete it", client.delete("/api/delete/announcement?title=Staff meeting", headers=H["sara"]).status_code == 403)
check("teachers can't use the admin's delete", client.delete(f"/api/admin/announcements/{ID['Staff meeting']}", headers=H["sara"]).status_code == 403)
check("the admin can remove a teacher's announcement", client.delete(f"/api/admin/announcements/{ID['5-B duty']}", headers=H["root"]).status_code == 200 and "5-B duty" not in titles("omar"))
check("and their own", client.delete(f"/api/admin/announcements/{ID['Staff meeting']}", headers=H["root"]).status_code == 200)
check("deleting again says not found", client.delete(f"/api/admin/announcements/{ID['Staff meeting']}", headers=H["root"]).status_code == 404)

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
