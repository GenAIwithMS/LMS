from flask import Blueprint

home_bp = Blueprint("home",__name__)

@home_bp.route("/")
def home():
    return "hello"


@home_bp.route("/about")
def about():
    return "about Page"