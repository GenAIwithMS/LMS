"""Login rules, logout, rate limits, allowed websites, start-up checks and paging. In-memory SQLite."""
import os, sys, datetime
os.environ.update(RATELIMIT_ENABLED="true", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:", CORS_ORIGINS="http://localhost:3000")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from src import create_app
from src.db import db
from src.models import Admin, Teacher, Section, Student
import src.routes.chatbot as chat_route
from langchain_core.messages import AIMessage

fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond:
        fails.append(name)

print("--- Start-up checks")
os.environ["JWT_SECRET_KEY"] = "short"
try:
    create_app(); started = True
except RuntimeError as error:
    started = False; message = str(error)
check("refuses to start with a short JWT secret", not started and "32 characters" in message)
os.environ["JWT_SECRET_KEY"] = "x" * 40

app = create_app()
client = app.test_client()

def make(cls, name, uname, **kw):
    u = cls(name=name, username=uname, email=f"{uname}@x.com", **kw); u.set_password("secret1"); return u

with app.app_context():
    db.create_all()
    admin = make(Admin, "Root", "root"); sara = make(Teacher, "Sara", "sara")
    db.session.add_all([admin, sara]); db.session.commit()
    sec = Section(name="A", teacher_id=sara.id); db.session.add(sec); db.session.commit()
    for number in range(1, 8):
        db.session.add(make(Student, f"Student {number}", f"s{number}", section_id=sec.id))
    db.session.commit()

def login(email, password="secret1", ip="10.0.0.1"):
    return client.post("/api/login", json={"email": email, "password": password}, environ_base={"REMOTE_ADDR": ip})

print("--- Login")
check("login lasts 30 minutes", app.config["JWT_ACCESS_TOKEN_EXPIRES"] == datetime.timedelta(minutes=30))
r1 = login("nobody@x.com", ip="10.0.0.2"); r2 = login("root@x.com", "wrongpass", ip="10.0.0.2")
check("same message for unknown email and wrong password",
      r1.status_code == r2.status_code == 401 and r1.get_json()["message"] == r2.get_json()["message"] == "Invalid email or password",
      (r1.get_json(), r2.get_json()))

token = login("root@x.com", ip="10.0.0.3").get_json()["token"]
headers = {"Authorization": f"Bearer {token}"}
check("token works before logout", client.get("/api/account", headers=headers).status_code == 200)
check("logout works", client.post("/api/logout", headers=headers).status_code == 200)
r = client.get("/api/account", headers=headers)
check("token is blocked after logout", r.status_code == 401 and "logged out" in r.get_json()["message"], r.get_json())

print("--- Rate limits")
codes = []
for attempt in range(12):
    codes.append(login("root@x.com", "wrongpass", ip="10.0.0.9").status_code)
check("11th login attempt in a minute is refused", codes[:10] == [401] * 10 and codes[10] == 429, codes)
check("another address can still log in", login("root@x.com", ip="10.0.0.10").status_code == 200)

class StubGraph:
    def invoke(self, state, config):
        return {"messages": state["messages"] + [AIMessage(content="ok")]}
chat_route.create_chatbot_graph = lambda role: StubGraph()
sara_token = login("sara@x.com", ip="10.0.0.11").get_json()["token"]
chat_codes = []
for attempt in range(21):
    chat_codes.append(client.post("/api/chat", json={"message": "hi"}, headers={"Authorization": f"Bearer {sara_token}"}).status_code)
check("21st chat message in a minute is refused", chat_codes[:20] == [200] * 20 and chat_codes[20] == 429, chat_codes[-3:])

print("--- Allowed websites (CORS)")
r = client.options("/api/login", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
check("our frontend is allowed", r.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000", r.headers.get("Access-Control-Allow-Origin"))
r = client.options("/api/login", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"})
check("other websites are not allowed", r.headers.get("Access-Control-Allow-Origin") is None, r.headers.get("Access-Control-Allow-Origin"))

print("--- Paging")
admin_token = login("root@x.com", ip="10.0.0.12").get_json()["token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}
r = client.get("/api/get/student", headers=admin_headers)
check("without ?page the whole list comes back as before", isinstance(r.get_json(), list) and len(r.get_json()) == 7)
r = client.get("/api/get/student?page=2&per_page=3", headers=admin_headers)
body = r.get_json()
check("?page=2&per_page=3 gives students 4-6", [s["username"] for s in body["data"]] == ["s4", "s5", "s6"] and body["total"] == 7 and body["pages"] == 3, body)
r = client.get("/api/get/subjects?page=1&per_page=5", headers=admin_headers)
check("paging works for lists inside 'data' too", r.status_code == 200 and "pages" in r.get_json(), r.get_json())

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
