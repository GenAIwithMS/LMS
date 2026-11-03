import json
from flask import g
from flask_jwt_extended import get_jwt, get_jwt_identity
from src.db import db
from src.models import PendingAction


# Deletes and edits asked for in the chat are never done straight away. The tool
# saves a PendingAction and the user sees Confirm / Cancel buttons. Only when
# the user clicks Confirm does /api/chat/confirm run the tool again, this time
# with g.confirmed_action set, and the change really happens.


def is_confirmed():
    """True only while /api/chat/confirm is running an action the user confirmed."""
    return g.get("confirmed_action", False)


def ask_to_confirm(tool_name, tool_args, description):
    """Save the delete or edit as waiting for the user, and tell the model what to say."""
    token = get_jwt()

    action = PendingAction(
        user_id=int(get_jwt_identity()),
        user_role=token.get("role"),
        tool_name=tool_name,
        tool_args=json.dumps(tool_args),
        description=description,
    )
    db.session.add(action)
    db.session.commit()

    return {
        "status": "needs_confirmation",
        "message": f"Nothing has been changed yet. Tell the user: \"{description}\" needs their confirmation, "
                   "and that they must click Confirm or Cancel below this message. Do not call this tool again.",
        "action_id": action.id
    }


def describe_changes(tool_args, skip):
    """Turn the new values into text like: name → 'Ali Khan', email → 'ali@x.com'.

    skip lists the arguments that only say WHICH record to change (like student_id).
    """
    parts = []
    for key, value in tool_args.items():
        if key in skip or value is None:
            continue
        text = str(value)
        if len(text) > 60:
            text = text[:57] + "..."
        parts.append(f"{key.replace('_', ' ')} → '{text}'")

    if not parts:
        return "no changes"
    return ", ".join(parts)
