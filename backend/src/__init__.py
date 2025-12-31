from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from src.db import db
from src.extention import bcrypt , jwt
from src.models import Student, Teacher, Admin, Assignment, Attendance,Result,Subject,Course,Announcement,AssignmentSubmission,Enrollment,Event,Message,Section

from src.routes import home_bp,auth_bp,student_bp,teacher_bp,admin_bp,assignment_bp,subject_bp,result_bp,section_bp,assignment_submission_bp,announcement_bp,chatbot_bp,course_bp,enrollment_bp,event_bp,attendance_bp

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