"""Smoke test for the agent quick fixes. No LLM calls; uses in-memory SQLite."""
import os, re, sys
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
from src.models import Teacher, Course, Subject, Section, Student, Result
from flask_jwt_extended import create_access_token
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

app = create_app()
fails = []
def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  -> {extra}" if extra else ""))
    if not cond:
        fails.append(name)

with app.app_context():
    db.create_all()
    t = Teacher(name="Sara", username="sara", email="sara@x.com"); t.set_password("pw")
    db.session.add(t); db.session.commit()
    c = Course(name="CS", course_code="CS1", description="d", teacher_id=t.id)
    sec = Section(name="A", teacher_id=t.id)
    db.session.add_all([c, sec]); db.session.commit()
    sub = Subject(name="Maths", teacher_id=t.id, course_id=c.id)
    s1 = Student(name="Ali", username="ali", email="ali@x.com", section_id=sec.id); s1.set_password("pw")
    s2 = Student(name="Bilal", username="bilal", email="b@x.com", section_id=sec.id); s2.set_password("pw")
    db.session.add_all([sub, s1, s2]); db.session.commit()
    r2 = Result(subject_id=sub.id, student_id=s2.id, total_marks=20, obtained_marks=15, exam_type="midterm", grade="B")
    db.session.add(r2); db.session.commit()
    ids = dict(teacher=t.id, s1=s1.id, s2=s2.id, r2=r2.id)

def as_user(role, uid):
    tok = create_access_token(identity=str(uid), additional_claims={"role": role})
    return app.test_request_context(headers={"Authorization": f"Bearer {tok}"})

from src.agent import tools as T
from src.agent.tools_list import admin_tools, teacher_tools, student_tools
from src.agent import prompts, main

# 1. Tool sets and schemas
names = lambda ts: {t.name for t in ts}
print(f"tool counts: admin={len(admin_tools)} teacher={len(teacher_tools)} student={len(student_tools)}")
check("student tools", names(student_tools) == {"get_my_submissions", "get_my_attendance", "get_my_results", "get_announcements", "get_announcement"}, sorted(names(student_tools)))
teacher_only_writes = {"create_announcement", "update_announcement", "remove_announcement", "create_assignment", "update_assignment", "remove_assignment", "mark_attendance", "update_attendance_tool", "remove_attendance", "update_submission_tool"}
check("admin has no teacher-only write tools", not (names(admin_tools) & teacher_only_writes))
check("create_teacher schema", set(T.create_teacher.args) == {"name", "username", "email", "password"}, list(T.create_teacher.args))
check("update_teacher_tool has no subject arg", "subject" not in T.update_teacher_tool.args)
check("get_my_results has no args (identity from JWT)", T.get_my_results.args == {}, T.get_my_results.args)

# 2. Prompts only mention tools that exist
all_tool_names = {v.name for v in vars(T).values() if hasattr(v, "args_schema") and hasattr(v, "name")}
for role, p in [("admin", prompts.admin_system_prompt), ("teacher", prompts.teacher_system_prompt), ("student", prompts.student_system_prompt)]:
    mentioned = set(re.findall(r"\b(?:get|check|create|update|remove)_[a-z_]+\b", p))
    check(f"{role} prompt mentions only real tools", mentioned <= all_tool_names, sorted(mentioned - all_tool_names))

# 3. Tool calls return readable data
with app.app_context():
    with as_user("admin", 1):
        r = T.create_teacher.invoke({"name": "Omar", "username": "omar", "email": "omar@x.com", "password": "secret"})
        check("create_teacher works", isinstance(r, dict) and r.get("status") == "success", r)
        r = T.create_teacher.invoke({"name": "Omar2", "username": "omar", "email": "omar2@x.com", "password": "secret"})
        check("duplicate teacher reported as failed", r.get("status") == "failed", r)
        r = T.create_course.invoke({"name": "Physics", "description": "d", "course_code": "PH1", "teacher_name": "Nobody"})
        check("missing teacher reported as failed dict", isinstance(r, dict) and r.get("status") == "failed", r)
        r = T.get_teachers.invoke({})
        check("list result wrapped with count", isinstance(r, dict) and r.get("count") == 2, str(r)[:80])
        r = T.get_announcements.invoke({})
        check("get_announcements returns data, not a Response", isinstance(r, dict) and "data" in r, str(r)[:80])
    with as_user("student", ids["s1"]):
        r = T.get_my_results.invoke({})
        check("student sees only own results (none)", r.get("count") == 0, r)
        r = T.get_result.invoke({"result_id": ids["r2"]})
        check("student blocked from reading other result by id", r.get("status") == "failed", r)
        r = T.get_my_submissions.invoke({})
        check("get_my_submissions returns readable data", isinstance(r, dict), str(r)[:80])
        r = T.get_my_attendance.invoke({})
        check("get_my_attendance with no records returns empty list", r == {"status": "success", "count": 0, "data": []}, r)
    with as_user("student", ids["s2"]):
        r = T.get_my_results.invoke({})
        check("student 2 sees own result", r.get("count") == 1, str(r)[:80])

# 4. System prompt is sent on every model call
class RecordingModel:
    def __init__(self): self.calls = []
    def invoke(self, msgs):
        self.calls.append(msgs); return AIMessage(content="ok")

rec = RecordingModel()
history = [HumanMessage("hi"), AIMessage("hello"), HumanMessage("show results")]
after_tool = history + [AIMessage(content="", tool_calls=[{"name": "get_results", "args": {}, "id": "1"}]), ToolMessage("[]", tool_call_id="1")]
for msgs in ([HumanMessage("hi")], history, after_tool):
    main.agent_node({"messages": msgs, "user_role": "admin"}, rec, "SYS")
check("system prompt first on every call", all(isinstance(c[0], SystemMessage) and c[0].content.startswith("SYS") for c in rec.calls))
check("exactly one system message per call", all(sum(isinstance(m, SystemMessage) for m in c) == 1 for c in rec.calls))

# 5. Graphs build once per role; ToolNode runs tools inside the Flask request
g1 = main.create_chatbot_graph("teacher"); g2 = main.create_chatbot_graph("teacher")
check("graph cached per role", g1 is g2)
check("all role graphs build", all(main.create_chatbot_graph(r) for r in ("admin", "student")))
check("model settings", main.model.temperature < 1e-6 and main.model.reasoning_format == "hidden", (main.model.temperature, main.model.reasoning_format))

from langgraph.prebuilt import ToolNode
with app.app_context():
    with as_user("student", ids["s2"]):
        from langgraph.graph import StateGraph, MessagesState, START, END
        gb = StateGraph(MessagesState)
        gb.add_node("tools", ToolNode(student_tools, handle_tool_errors=True))
        gb.add_edge(START, "tools"); gb.add_edge("tools", END)
        out = gb.compile().invoke({"messages": [AIMessage(content="", tool_calls=[
            {"name": "get_my_results", "args": {}, "id": "a"},
            {"name": "check_subject_exists", "args": {}, "id": "b"}])]})
        msgs = [m for m in out["messages"] if isinstance(m, ToolMessage)]
        check("ToolNode runs tool with JWT context (parallel calls)", '"count": 1' in msgs[0].content, msgs[0].content[:80])
        check("invented tool name returns an error message", "not a valid tool" in msgs[1].content.lower() or "error" in msgs[1].content.lower(), msgs[1].content[:80])

print("\nFAILED:" if fails else "\nALL PASSED", fails if fails else "")
sys.exit(1 if fails else 0)
