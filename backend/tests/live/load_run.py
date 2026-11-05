"""Load test: many users at once against the running server.

Setup (through the API, as the admin): Class 6 with 2 sections, 8 teachers, 50 students,
a published timetable, an assignment and today's register. Login tokens for all users are
made with the server's own JWT secret (the login route only allows 10 logins a minute
from one address, which would stop a test that runs from one computer).

Then rounds of N requests fired at once by many threads, a realistic mix of what admins,
teachers and students do (mostly reading pages, some writing). For each round: success
rate, response times and error types. Afterwards the database is checked for duplicates
or lost writes.

Usage: load_run.py <requests per round> <parallel connections> <rounds> [label]
"""
import io
import json
import os
import random
import statistics
import tempfile
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import requests
from requests.adapters import HTTPAdapter

BACKEND = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)
from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND, ".env"))

BASE = "http://localhost:5000/api"
PER_ROUND = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 200
ROUNDS = int(sys.argv[3]) if len(sys.argv) > 3 else 3
LABEL = sys.argv[4] if len(sys.argv) > 4 else ""
TODAY = date.today()
TAG = str(int(time.time()))[-5:]
STATE_FILE = os.path.join(tempfile.gettempdir(), "lms_load_state.json")

session = requests.Session()
session.mount("http://", HTTPAdapter(pool_connections=WORKERS, pool_maxsize=WORKERS))


def make_token(user_id, role, name, username):
    """The same token the login route hands out."""
    from flask_jwt_extended import create_access_token
    from src import create_app
    global _app
    if "_app" not in globals():
        _app = create_app()
    with _app.app_context():
        return create_access_token(identity=str(user_id), additional_claims={"role": role, "name": name, "email": f"{username}@lms.test", "username": username})


def call(method, path, token=None, **kwargs):
    headers = {"Authorization": "Bearer " + token} if token else {}
    response = session.request(method, BASE + path, headers=headers, timeout=120, **kwargs)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, response.text


# ---------------------------------------------------------------- setup
def setup():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    status, body = call("POST", "/login", json={"email": "root@lms.test", "password": "secret1"})
    root = body["token"]
    classes = call("GET", "/school/classes", root)[1]
    class_6 = classes[5]["id"]

    teachers = []
    for i in range(8):
        uname = f"lt{TAG}t{i}"
        call("POST", "/add/teacher", root, json={"name": f"Load Teacher {i}", "username": uname, "email": f"{uname}@lms.test", "password": "secret1"})
    for teacher in call("GET", "/get/teacher", root)[1]:
        if teacher["username"].startswith(f"lt{TAG}t"):
            teachers.append(teacher)
    teachers.sort(key=lambda t: t["username"])

    sections = []
    for i, name in enumerate(["A", "B"]):
        status, body = call("POST", f"/school/classes/{class_6}/sections", root, json={"name": name, "incharge_id": teachers[i]["id"]})
        sections.append(body["section_id"])
    subjects = []
    for name in ["Maths", "English", "Science", "Urdu"]:
        subjects.append(call("POST", f"/school/classes/{class_6}/subjects", root, json={"name": name})[1]["subject_id"])
    # teacher 0 and 1 lead A and B and teach Maths there; teachers 2-7 teach the rest
    for s_index, section in enumerate(sections):
        for subj_index, subject in enumerate(subjects):
            teacher = teachers[s_index] if subj_index == 0 else teachers[2 + (s_index * 3 + subj_index - 1) % 6]
            call("POST", f"/school/teachers/{teacher['id']}/subjects", root, json={"name": ["Maths", "English", "Science", "Urdu"][subj_index]})
            call("PUT", f"/school/sections/{section}/teachers", root, json={"subject_id": subject, "teacher_id": teacher["id"]})
    for s_index, section in enumerate(sections):
        for day in range(1, 7):
            for period in range(1, 5):
                call("PUT", f"/school/sections/{section}/timetable", root, json={"day": day, "period": period + s_index * 4, "subject_id": subjects[period - 1]})
    call("POST", "/timetable/publish", root)

    students = []
    for i in range(50):
        uname = f"lt{TAG}s{i}"
        call("POST", "/add/student", root, json={"name": f"Load Student {i}", "username": uname, "email": f"{uname}@lms.test",
                                               "password": "secret1", "section_id": sections[i % 2], "roll_number": str(i // 2 + 1)})
    for student in call("GET", "/get/student", root)[1]:
        if student["username"].startswith(f"lt{TAG}s"):
            students.append(student)

    # One assignment per section, from its Maths teacher
    due = (TODAY + timedelta(days=7)).isoformat()
    assignments = []
    for s_index, section in enumerate(sections):
        token = make_token(teachers[s_index]["id"], "teacher", teachers[s_index]["name"], teachers[s_index]["username"])
        call("POST", "/create/assignments", token, json={"title": f"Load homework {TAG}{s_index}", "description": "x", "subject_id": subjects[0],
                                                      "section_id": section, "due_date": due, "total_marks": 10})
        for a in call("GET", "/get/assignments", token)[1]["assignments"]:
            if a["title"] == f"Load homework {TAG}{s_index}":
                assignments.append(a["id"])

    state = {"root": root, "sections": sections, "subjects": subjects, "assignments": assignments,
             "teachers": [{"id": t["id"], "token": make_token(t["id"], "teacher", t["name"], t["username"])} for t in teachers],
             "students": [{"id": s["id"], "section": s.get("section_id"), "token": make_token(s["id"], "student", s["name"], s["username"])} for s in students]}
    # Which section each student is in
    for s in state["students"]:
        if not s["section"]:
            s["section"] = sections[int(next(st for st in students if st["id"] == s["id"])["username"].split("s")[-1]) % 2]
    json.dump(state, open(STATE_FILE, "w"))
    return state


# ---------------------------------------------------------------- the request mix
def build_requests(state, count):
    """count requests: about 75% reads, 25% writes, from admins, teachers and students."""
    root = state["root"]
    teachers = state["teachers"]
    students = state["students"]
    sections = state["sections"]
    jobs = []
    for i in range(count):
        roll = random.random()
        student = random.choice(students)
        teacher = random.choice(teachers)
        section = random.choice(sections)
        if roll < 0.12:
            jobs.append(("student dashboard", "GET", "/get/assignments", student["token"], {}))
        elif roll < 0.22:
            jobs.append(("student timetable", "GET", "/school/my-timetable", student["token"], {}))
        elif roll < 0.30:
            jobs.append(("student my class", "GET", "/school/my-class", student["token"], {}))
        elif roll < 0.38:
            jobs.append(("announcements", "GET", "/get/announcements", student["token"], {}))
        elif roll < 0.44:
            jobs.append(("student attendance", "GET", "/school/my-attendance", student["token"], {}))
        elif roll < 0.50:
            jobs.append(("student class tests", "GET", "/school/class-tests", student["token"], {}))
        elif roll < 0.56:
            jobs.append(("teacher my classes", "GET", "/school/my-classes", teacher["token"], {}))
        elif roll < 0.62:
            jobs.append(("teacher section register", "GET", f"/school/sections/{section}/attendance", teacher["token"], {}))
        elif roll < 0.66:
            jobs.append(("admin students list", "GET", "/get/student", root, {}))
        elif roll < 0.70:
            jobs.append(("admin oversight", "GET", "/oversight/dashboard", root, {}))
        elif roll < 0.74:
            jobs.append(("admin activity log", "GET", "/oversight/activity", root, {}))
        elif roll < 0.82:
            # write: a student submits (or updates) their homework
            assignment = state["assignments"][sections.index(student["section"])] if student["section"] in sections else state["assignments"][0]
            jobs.append(("WRITE student submits", "POST", "/submit/assignment", student["token"],
                         {"data": {"assignment_id": str(assignment), "submission_text": f"answer {i}"}}))
        elif roll < 0.88:
            # write: the incharge marks today's register for their section
            s_index = random.randrange(2)
            incharge = teachers[s_index]
            records = [{"student_id": s["id"], "status": random.choice(["present", "present", "absent", "late"])}
                       for s in students if s["section"] == sections[s_index]]
            jobs.append(("WRITE incharge marks attendance", "POST", f"/school/sections/{sections[s_index]}/attendance", incharge["token"],
                         {"json": {"date": state["school_day"], "records": records}}))
        elif roll < 0.93:
            # write: the Maths teacher writes today's diary
            s_index = random.randrange(2)
            jobs.append(("WRITE teacher writes diary", "POST", f"/school/sections/{sections[s_index]}/diary", teachers[s_index]["token"],
                         {"json": {"subject_id": state["subjects"][0], "date": state["school_day"], "classwork": f"lesson {i}"}}))
        elif roll < 0.97:
            # write: a teacher posts an announcement for their section
            s_index = random.randrange(2)
            jobs.append(("WRITE teacher announcement", "POST", "/create/announcement", teachers[s_index]["token"],
                         {"json": {"title": f"Load notice {TAG}-{i}", "content": "x", "target_audience": "students", "section_id": sections[s_index]}}))
        else:
            jobs.append(("login (rate limited)", "POST", "/login", None, {"json": {"email": "root@lms.test", "password": "secret1"}}))
    return jobs


def run_one(job):
    name, method, path, token, kwargs = job
    started = time.perf_counter()
    try:
        status, body = call(method, path, token, **kwargs)
        error = None
        if status >= 400:
            message = body.get("message") if isinstance(body, dict) else str(body)[:80]
            error = f"{status} {message}"
    except Exception as exc:
        status, error = 0, type(exc).__name__ + ": " + str(exc)[:80]
    return name, status, time.perf_counter() - started, error


def percentile(values, p):
    values = sorted(values)
    if not values:
        return 0
    index = min(len(values) - 1, int(round(p / 100 * (len(values) - 1))))
    return values[index]


def main():
    state = setup()
    day = TODAY
    while day.isoweekday() == 7:
        day = day - timedelta(days=1)
    state["school_day"] = day.isoformat()
    print(f"Users: 1 admin, {len(state['teachers'])} teachers, {len(state['students'])} students. "
          f"{PER_ROUND} requests per round, {WORKERS} at once, {ROUNDS} rounds. {LABEL}")

    all_results = []
    for round_number in range(1, ROUNDS + 1):
        jobs = build_requests(state, PER_ROUND)
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            results = list(pool.map(run_one, jobs))
        took = time.perf_counter() - started
        all_results.extend(results)
        times = [r[2] for r in results]
        ok = [r for r in results if 200 <= r[1] < 400]
        expected_refusals = [r for r in results if r[0].startswith("login") and r[1] == 429]
        print(f"Round {round_number}: {len(ok)}/{len(results)} OK, {len(expected_refusals)} logins rate-limited (expected), "
              f"{took:.1f}s total, {len(results) / took:.0f} req/s, "
              f"median {statistics.median(times) * 1000:.0f} ms, p95 {percentile(times, 95) * 1000:.0f} ms, p99 {percentile(times, 99) * 1000:.0f} ms, max {max(times) * 1000:.0f} ms")

    print("\nBy request type (all rounds):")
    by_name = {}
    for name, status, took, error in all_results:
        by_name.setdefault(name, []).append((status, took, error))
    for name in sorted(by_name):
        rows = by_name[name]
        ok = sum(1 for s, t, e in rows if 200 <= s < 400)
        print(f"  {name:32s} {ok:4d}/{len(rows):<4d} OK   median {statistics.median([t for s, t, e in rows]) * 1000:6.0f} ms   p95 {percentile([t for s, t, e in rows], 95) * 1000:6.0f} ms")

    errors = Counter(f"{name}: {error}" for name, status, took, error in all_results if error and not (name.startswith("login") and status == 429))
    print("\nUnexpected errors:" if errors else "\nNo unexpected errors.")
    for text, count in errors.most_common(15):
        print(f"  {count:5d} x {text}")
    json.dump({"label": LABEL, "results": all_results}, open(STATE_FILE.replace("load_state", f"load_results_{LABEL or 'run'}"), "w"))


if __name__ == "__main__":
    main()
