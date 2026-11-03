"""Create the LMS admin account. Run this once during setup:

    cd backend
    python create_admin.py

The LMS has a single admin. This script refuses to run if an admin already exists.
The password is typed in hidden and saved as a bcrypt hash, never as plain text.
"""
from getpass import getpass

from src import create_app
from src.db import db
from src.models import Admin
from src.services.users import is_email_taken, is_username_taken


app = create_app()

with app.app_context():
    existing_admin = Admin.query.first()
    if existing_admin:
        print(f"An admin already exists (username: {existing_admin.username}). Nothing was changed.")
        raise SystemExit(1)

    print("Create the LMS admin account")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = getpass("Password (min 8 characters): ")
    confirm_password = getpass("Confirm password: ")

    if not name or not email or not username:
        print("Name, email and username are all required.")
        raise SystemExit(1)

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        raise SystemExit(1)

    if password != confirm_password:
        print("Passwords do not match.")
        raise SystemExit(1)

    if is_email_taken(email):
        print("That email is already used by another account.")
        raise SystemExit(1)

    if is_username_taken(username):
        print("That username is already used by another account.")
        raise SystemExit(1)

    admin = Admin(name=name, email=email, username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"Admin '{username}' created. You can now log in with {email}.")
