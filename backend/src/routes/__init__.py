from .home import home_bp
from .auth import auth_bp
from .student import student_bp
from .teacher import teacher_bp
from .admin import admin_bp 
from .assignments import assignment_bp
from .subject import subject_bp
from .result import result_bp
from .section import section_bp
from .assignment_submission import assignment_submission_bp
from .announcement import announcement_bp
from .chatbot import chatbot_bp
from .course import course_bp
from .enrollment import enrollment_bp
from .event import event_bp
from .attendance import attendance_bp

__all__ = ["home_bp","auth_bp","student_bp","teacher_bp","admin_bp","assignment_bp","subject_bp","result_bp","section_bp","assignment_submission_bp","announcement_bp","chatbot_bp","course_bp","enrollment_bp","event_bp","attendance_bp"]

