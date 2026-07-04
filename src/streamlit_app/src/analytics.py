import logging
from datetime import datetime, timezone

from google.cloud import firestore

_db = None
FIRESTORE_TIMEOUT_SECONDS = 5.0


def _get_client():
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db


def log_login(user_info: dict):
    """Record a login in Firestore, mirroring the users/{email}/... layout
    the existing chat-logging Cloud Function already writes to."""
    email = user_info.get("email")
    if not email:
        return
    try:
        db = _get_client()
        timestamp = datetime.now(timezone.utc).isoformat()
        db.document(f"users/{email}/logins/{timestamp}").set(
            {"user_info": user_info, "timestamp": timestamp},
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        )
        db.document(f"users/{email}").set(
            {"last_login": timestamp, "login_count": firestore.Increment(1)},
            merge=True,
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        )
    except Exception as e:
        logging.error(f"Failed to log login for {email}: {e}")


def log_interaction(user_info: dict, question: str, answer: str):
    """Record a chat interaction in Firestore, in the same
    users/{email}/interactions/{timestamp} layout the old Cloud Function
    (prompt-receptor, called via postMessage from public/index.html) wrote
    to - now written directly, since the app no longer depends on running
    inside that iframe to know who's logged in."""
    email = user_info.get("email")
    if not email:
        return
    try:
        db = _get_client()
        timestamp = datetime.now(timezone.utc).isoformat()
        db.document(f"users/{email}/interactions/{timestamp}").set(
            {
                "prompt_data": {"question": question, "answer": answer, "timestamp": timestamp},
                "user_info": user_info,
            },
            timeout=FIRESTORE_TIMEOUT_SECONDS,
        )
    except Exception as e:
        logging.error(f"Failed to log interaction for {email}: {e}")
