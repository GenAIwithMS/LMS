from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, verify_jwt_in_request
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()

# Limits how often the same visitor can call an endpoint (for example login),
# so passwords can't be guessed quickly and the chatbot can't run up API costs.
# No limit applies unless a route sets one.
limiter = Limiter(key_func=get_remote_address)


def logged_in_user_key():
    """Rate-limit key for logged-in routes: the user's role and id (falls back to the IP)."""
    try:
        verify_jwt_in_request()
        return f"{get_jwt().get('role')}:{get_jwt_identity()}"
    except Exception:
        return get_remote_address()
