from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from datetime import timedelta
from dotenv import load_dotenv
from src.db import db, pakistan_time_naive
from src.services.pagination import paginate_list_response
from src.extention import bcrypt , jwt, limiter, migrate
from src.models import Student, Teacher, Admin, Assignment, Attendance,Result,Subject,Course,Announcement,AssignmentSubmission,Enrollment,Event,Message,Section,RevokedToken

from src.routes import home_bp,auth_bp,student_bp,teacher_bp,admin_bp,assignment_bp,subject_bp,result_bp,section_bp,assignment_submission_bp,announcement_bp,chatbot_bp,course_bp,enrollment_bp,event_bp,attendance_bp,school_bp,teaching_bp,exam_bp

load_dotenv()


def check_settings():
    """Stop at start-up with a clear message if a required setting is missing or unsafe."""
    secret_key = os.getenv("JWT_SECRET_KEY") or ""
    if len(secret_key) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY in .env must be at least 32 characters. "
            "Generate one with:  python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if not os.getenv("DATABASE_URI"):
        raise RuntimeError("DATABASE_URI is missing from .env")


def get_allowed_origins():
    """Websites allowed to call the API, from CORS_ORIGINS in .env (comma separated)."""
    origins_text = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = []
    for origin in origins_text.split(","):
        if origin.strip():
            origins.append(origin.strip())
    return origins


def create_app():
    check_settings()

    # static_folder=None: Flask serves no public files. Older versions saved uploaded
    # submissions in src/static, where anyone could download them without logging in.
    app = Flask(__name__, static_folder=None)

    # Behind a reverse proxy (nginx etc.), every request seems to come from the
    # proxy. Set TRUSTED_PROXY_COUNT=1 (one proxy) so the real visitor address is
    # used for rate limits. Leave it at 0 when the app is reached directly,
    # otherwise visitors could fake their address.
    proxy_count = int(os.getenv("TRUSTED_PROXY_COUNT", "0"))
    if proxy_count > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxy_count, x_proto=proxy_count, x_host=proxy_count)

    # Safe headers on every API answer
    @app.after_request
    def add_security_headers(response):
        # Don't let the browser guess a file's type (an uploaded file can't run as a web page)
        response.headers["X-Content-Type-Options"] = "nosniff"
        # The API never needs to be shown inside another site's frame
        response.headers["X-Frame-Options"] = "DENY"
        # The API only sends data and files, never pages with scripts
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

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

    # Any error not handled above. Known HTTP errors (404, 405, ...) keep their
    # code; an unexpected crash becomes a plain 500 message. Either way the
    # browser gets JSON it can show, never an HTML error page or Python details.
    @app.errorhandler(Exception)
    def unexpected_error(error):
        if isinstance(error, HTTPException):
            return jsonify({
                "message": error.description,
                "status": "failed"
            }), error.code

        db.session.rollback()
        app.logger.exception("Unexpected error on %s %s", request.method, request.path)
        return jsonify({
            "message": "Something went wrong on the server. Please try again.",
            "status": "failed"
        }), 500

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            "message": "Too many requests. Please wait a minute and try again.",
            "status": "failed"
        }), 429

    # Only our own frontend may call the API (not any website)
    CORS(app, 
         resources={r"/api/*": {
             "origins": get_allowed_origins(),
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             # Lets the browser read the file name of downloaded submissions
             "expose_headers": ["Content-Disposition"]
         }}, 
         supports_credentials=True) 

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # A login lasts a fixed 30 minutes (change with JWT_EXPIRES_MINUTES in .env).
    # After that the user must log in again.
    login_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "30"))
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=login_minutes)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI"
    )

    # Rate limits are on unless RATELIMIT_ENABLED=false (only for automated tests).
    # With several server processes, point RATELIMIT_STORAGE_URI at Redis so they share counts.
    app.config["RATELIMIT_ENABLED"] = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    app.config["RATELIMIT_STORAGE_URI"] = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    # render_as_batch: lets migrations change tables on SQLite too (used by the tests)
    migrate.init_app(app, db, render_as_batch=True)

    # Any list can be split into pages with ?page=&per_page= (see services/pagination.py)
    app.after_request(paginate_list_response)

    # A token that was logged out can't be used again, even before it expires
    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_header, jwt_payload):
        now = pakistan_time_naive()
        revoked = RevokedToken.query.filter(RevokedToken.jti == jwt_payload["jti"],
                                            RevokedToken.revoked_at <= now).first()
        return revoked is not None

    @jwt.revoked_token_loader
    def revoked_token_answer(jwt_header, jwt_payload):
        return jsonify({
            "message": "You have been logged out. Please log in again.",
            "status": "failed"
        }), 401
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
    app.register_blueprint(school_bp)
    app.register_blueprint(teaching_bp)
    app.register_blueprint(exam_bp)


    # Tables are created and updated with migrations, not db.create_all():
    #   flask --app app db upgrade
    # (create_all never changes existing tables, so new columns or rules were missed.)

    return app