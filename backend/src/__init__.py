from flask import Flask, jsonify
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
from src.db import db
from src.extention import bcrypt , jwt
from src.models import Student, Teacher, Admin, Assignment, Attendance,Result,Subject,Course,Announcement,AssignmentSubmission,Enrollment,Event,Message,Section

from src.routes import home_bp,auth_bp,student_bp,teacher_bp,admin_bp,assignment_bp,subject_bp,result_bp,section_bp,assignment_submission_bp,announcement_bp,chatbot_bp,course_bp,enrollment_bp,event_bp,attendance_bp

load_dotenv()

def create_app():
    # static_folder=None: Flask serves no public files. Older versions saved uploaded
    # submissions in src/static, where anyone could download them without logging in.
    app = Flask(__name__, static_folder=None)

    # Largest upload allowed (10 MB). Bigger files get a 413 error.
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "message": "File is too large. The maximum size is 10 MB.",
            "status": "failed"
        }), 413
    
    @app.errorhandler(IntegrityError)
    def database_refused(error):
        # The database refused a change (for example a duplicate username, or a
        # delete that other records still need). Undo it so the next query works.
        db.session.rollback()
        return jsonify({
            "message": "This change conflicts with existing data, so it was not saved.",
            "status": "failed"
        }), 409

    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             # Lets the browser read the file name of downloaded submissions
             "expose_headers": ["Content-Disposition"]
         }}, 
         supports_credentials=True) 

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # How long a login lasts. The library default is only 15 minutes.
    login_hours = int(os.getenv("JWT_EXPIRES_HOURS", "8"))
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=login_hours)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI"
    )

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(assignment_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(section_bp)
    app.register_blueprint(assignment_submission_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(chatbot_bp)


    with app.app_context():
        db.create_all()

    return app