from src import create_app
from src.models import Admin, Announcement 

app = create_app()

if __name__ == "__main__":
    import os
    debug_mode = os.getenv("FLASK_DEBUG").lower() == "true"
    port = int(os.getenv("PORT"))
    app.run(debug=debug_mode, port=port)
