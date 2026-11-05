# Settings for running the backend in production with gunicorn:
#     gunicorn app:app
# (gunicorn reads this file by itself when started in the backend folder.)
import os

# Several processes, each answering several requests at once. With only one process and
# one thread (gunicorn's default), every visitor waits in a single queue.
workers = int(os.getenv("WEB_WORKERS", "4"))
threads = int(os.getenv("WEB_THREADS", "8"))
worker_class = "gthread"

bind = "0.0.0.0:" + os.getenv("PORT", "5000")

# A request that takes longer than this is stopped (file uploads and reports included)
timeout = 120

# Keep an idle connection open a little longer, so a browser reusing it doesn't find it closed
keepalive = 5


def on_starting(server):
    # The per-address rate limits are kept in each process's memory unless they are
    # stored in Redis. Account login protection is in the database, so it always works.
    if workers > 1 and os.getenv("RATELIMIT_STORAGE_URI", "memory://").startswith("memory"):
        server.log.warning("Rate limits are counted separately in each of the %s workers. "
                           "Set RATELIMIT_STORAGE_URI to a Redis address to share them.", workers)
