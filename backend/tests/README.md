# Backend tests

These check the security rules and the bug fixes: who can see and change what,
logins, uploads, the chatbot tools, and the error handling. They use a small
in-memory SQLite database and never call the AI model, so they need no MySQL
and no Groq key.

## Run

```bash
cd backend
pip install -r requirements.txt
pytest tests -v
```

Run one script on its own to see every check it makes:

```bash
python tests/checks/check_website_scoping.py
```

## Files

| File | What it checks |
|---|---|
| `check_security_fixes.py` | Admin setup, passwords, My Account, uploads, submission permissions |
| `check_website_scoping.py` | Teachers only reach their own data on the website; timestamps; login length |
| `check_crashes_and_forms.py` | Bad input gives clear errors instead of 500s; students' assignments; forms that pick students by ID |
| `check_unique_users.py` | Usernames and emails are unique across admins, teachers and students |
| `check_agent_tools.py` | Chatbot tools return readable results; system prompt; tool lists per role |
| `check_agent_scoping.py` | Chatbot tools only reach the user's own data; asks when names are shared |
| `check_chat_confirm.py` | Chat history is kept on the server; deletes need the user's Confirm |

When you add a feature, add checks to the matching file (or a new `check_*.py` file:
the runner picks it up automatically).
