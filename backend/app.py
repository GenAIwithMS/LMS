import os
from src import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode shows code and lets anyone run commands if the server is reachable,
    # so it is off unless FLASK_DEBUG=true is set in .env (only on your own computer).
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug_mode, port=port)
