"""Closing a tab blocks its login; security headers; proxy setting; chatbot asks before edits. In-memory SQLite."""
import os, sys, time
os.environ.update(RATELIMIT_ENABLED="true", GROQ_API_KEY="dummy", JWT_SECRET_KEY="x" * 40,
                  DATABASE_URI="sqlite:///:memory:", TRUSTED_PROXY_COUNT="0")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # the backend folder

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):  # let SQLite autoincrement BigInteger PKs
    return "INTEGER"

from src import create_app
from src.db import db
from src.models import Admin, Teacher, Section, Student
import src.routes.auth as auth_route
import src.routes.chatbot as chat_route
from src.agent import tools as T
from langchain_core.messages import AIMessage

fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {str(extra)[:110]}" if extra != "" else ""))
    if not cond:
        fails.append(name)

def make(cls, name, uname, **kw):
    u = cls(name=name, username=uname, email=f"{uname}@x.com", **kw); u.set_password("secret1"); return u

def setup(app):
    with app.app_context():
        db.create_all()
        admin = make(Admin, "Root", "root"); sara = make(Teacher, "Sara", "sara")
        db.session.add_all([admin, sara]); db.session.commit()
        sec = Section(name="A", teacher_id=sara.id); db.session.add(sec); db.session.commit()
        ali = make(Student, "Ali", "ali", section_id=sec.id); db.session.add(ali); db.session.commit()
        return ali.id

app = create_app()
client = app.test_client()
ALI = setup(app)

# Make the delay short so the check doesn't take 15 seconds
auth_route.CLOSING_DELAY_SECONDS = 1

def login(user, ip="10.0.0.1"):
    return client.post("/api/login", json={"email": f"{user}@x.com", "password": "secret1"},
                       environ_base={"REMOTE_ADDR": ip}).get_json()["token"]

def account_status(token):
    return client.get("/api/account", headers={"Authorization": f"Bearer {token}"}).status_code

print("--- Closing a tab")
token = login("root")
r = client.post("/api/logout/closing", data=token, content_type="text/plain")
check("closing signal is accepted", r.status_code == 200 and r.get_json()["status"] == "success", r.get_json())
check("login still works right after the signal (a refresh has time to cancel)", account_status(token) == 200)
time.sleep(1.5)
check("after the delay the token is blocked", account_status(token) == 401)

token = login("root", ip="10.0.0.2")
client.post("/api/logout/closing", data=token, content_type="text/plain")
r = client.post("/api/logout/stay", headers={"Authorization": f"Bearer {token}"})
check("refresh cancels the block", r.status_code == 200)
time.sleep(1.5)
check("after a refresh the login keeps working", account_status(token) == 200)

r = client.post("/api/logout/closing", data="not-a-token", content_type="text/plain")
check("a bad token in the closing signal is ignored, not an error", r.status_code == 200 and r.get_json()["status"] == "ignored")

token = login("root", ip="10.0.0.3")
client.post("/api/logout/closing", data=token, content_type="text/plain")
client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
check("a real logout after the closing signal blocks straight away", account_status(token) == 401)

print("--- Security headers on API answers")
r = client.get("/api/account", headers={"Authorization": f"Bearer {login('root', ip='10.0.0.4')}"})
check("nosniff", r.headers.get("X-Content-Type-Options") == "nosniff")
check("no framing", r.headers.get("X-Frame-Options") == "DENY")
check("API sends no runnable content", "default-src 'none'" in (r.headers.get("Content-Security-Policy") or ""))

print("--- Proxy setting")
def count_until_blocked(test_client, forwarded_for):
    codes = []
    for attempt in range(11):
        r = test_client.post("/api/login", json={"email": "root@x.com", "password": "wrongpass"},
                             headers={"X-Forwarded-For": forwarded_for}, environ_base={"REMOTE_ADDR": "192.168.1.1"})
        codes.append(r.status_code)
    return codes

# Without a trusted proxy, X-Forwarded-For is ignored: a visitor can't dodge the limit by faking it
codes_a = count_until_blocked(client, "1.1.1.1")
codes_b = count_until_blocked(client, "2.2.2.2")
check("without TRUSTED_PROXY_COUNT a faked X-Forwarded-For doesn't reset the limit", codes_a[-1] == 429 and codes_b[0] == 429, (codes_a[-1], codes_b[0]))

os.environ["TRUSTED_PROXY_COUNT"] = "1"
proxy_app = create_app()
setup(proxy_app)
proxy_client = proxy_app.test_client()
codes_a = count_until_blocked(proxy_client, "3.3.3.3")
codes_b = count_until_blocked(proxy_client, "4.4.4.4")
check("behind a trusted proxy each real visitor has their own limit", codes_a[-1] == 429 and codes_b[0] == 401, (codes_a[-1], codes_b[0]))
os.environ["TRUSTED_PROXY_COUNT"] = "0"

print("--- Chatbot asks before edits")
class StubGraph:
    def invoke(self, state, config):
        result = T.update_student_tool.invoke({"student_id": ALI, "name": "Ali Khan", "email": "ali.khan@x.com"})
        return {"messages": state["messages"] + [AIMessage(content=f"tool status: {result.get('status')}")]}
chat_route.create_chatbot_graph = lambda role: StubGraph()

admin_headers = {"Authorization": f"Bearer {login('root', ip='10.0.0.5')}"}
r = client.post("/api/chat", json={"message": "rename ali"}, headers=admin_headers)
body = r.get_json()
check("edit tool asks instead of saving", body["message"] == "tool status: needs_confirmation", body["message"])
description = body["pending_actions"][0]["description"] if body["pending_actions"] else ""
check("the card says exactly what will change",
      "student 'Ali'" in description and "name → 'Ali Khan'" in description and "email → 'ali.khan@x.com'" in description, description)
with app.app_context():
    check("nothing changed yet", Student.query.get(ALI).name == "Ali")
r = client.post("/api/chat/confirm", json={"action_id": body["pending_actions"][0]["id"], "approve": True}, headers=admin_headers)
check("confirm applies the edit", r.status_code == 200 and r.get_json()["message"].startswith("Confirmed and done"), r.get_json())
with app.app_context():
    student = Student.query.get(ALI)
    check("the student now has the new name and email", student.name == "Ali Khan" and student.email == "ali.khan@x.com", (student.name, student.email))

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
