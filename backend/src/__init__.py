from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from src.routes.home import home_bp
from src.routes.auth import auth
from src.routes.student import student_bp
from src.routes.teacher import teacher_bp
from src.routes.admin import admin_bp 
from src.routes.assignments import assignment_bp
from src.routes.subject import subject_bp
from src.routes.result import result_bp
from src.routes.section import section_bp
from src.routes.assignment_submission import assignment_submission_bp
from src.routes.announcement import announcement_bp
from src.routes.chatbot import chatbot_bp
from src.db import db
from src.routes.course import course_bp
from src.extention import bcrypt , jwt
from src.routes.enrollment import enrollment_bp
from src.routes.event import event_bp
from src.routes.attendance import attendance_bp

from src.models.student import Student
from src.models.teacher import Teacher
from src.models.admin import Admin
from src.models.assignment import Assignment
from src.models.attendance import Attendance
from src.models.result import Result
from src.models.subject import Subject
from src.models.course import Course
from src.models.announcement import Announcement
from src.models.assignment_submission import AssignmentSubmission
from src.models.enrollment import Enrollment
from src.models.event import Event
from src.models.message import Message
from src.models.section import Section

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"]
         }}, 
         supports_credentials=True) 

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI", 
        "mysql+pymysql://root:@localhost/llm_LMS"
    )

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth)
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