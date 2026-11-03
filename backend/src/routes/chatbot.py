import json
import logging

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from langgraph.errors import GraphRecursionError
from src.agent.main import create_chatbot_graph, ROLE_TOOLS
from src.models import ChatMessage, PendingAction
from src.db import db
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

# Maximum agent steps per message (each model call or tool round counts as one).
# Stops a confused model from looping and running up API costs.
AGENT_RECURSION_LIMIT = 15

# How many earlier messages the assistant sees. Older ones stay saved but aren't sent.
HISTORY_LIMIT = 20

GREETING = "Hello! I'm your LMS AI assistant. How can I help you today?"

chatbot_bp = Blueprint("chatbot", __name__)


def get_chat_user():
    """Return (role, user_id) of the logged-in user, or (None, None) if the role is not valid."""
    token = get_jwt()
    user_role = token.get("role")
    if user_role not in ["admin", "teacher", "student"]:
        return None, None
    return user_role, int(get_jwt_identity())


def save_chat_message(user_role, user_id, sender, content):
    message = ChatMessage(user_id=user_id, user_role=user_role, sender=sender, content=content)
    db.session.add(message)
    db.session.commit()


def get_waiting_actions(user_role, user_id):
    """Deletes this user still has to confirm or cancel."""
    actions = PendingAction.query.filter_by(user_id=user_id, user_role=user_role, status="waiting").order_by(PendingAction.id).all()
    result = []
    for action in actions:
        result.append({
            "id": action.id,
            "description": action.description
        })
    return result


@chatbot_bp.route("/api/chat", methods=["POST"])
@jwt_required()
def chat():
    """Chat with the LMS assistant based on user role."""

    user_role, user_id = get_chat_user()
    if not user_role:
        return jsonify({
            "message": "Invalid or missing user role",
            "status": "failed"
        }), 403

    try:
        data = request.get_json()
        if not data or not data.get("message"):
            return jsonify({
                "message": "Message is required",
                "status": "failed"
            }), 400

        user_message = data["message"]

        graph = create_chatbot_graph(user_role)

        # The conversation comes from our database, not from the browser,
        # so nobody can make up things the assistant "said" before.
        saved_messages = ChatMessage.query.filter_by(user_id=user_id, user_role=user_role).order_by(ChatMessage.id.desc()).limit(HISTORY_LIMIT).all()
        saved_messages.reverse()

        messages = []
        for saved in saved_messages:
            if saved.sender == "user":
                messages.append(HumanMessage(content=saved.content))
            else:
                messages.append(AIMessage(content=saved.content))

        # Add the new user message
        messages.append(HumanMessage(content=user_message))
        save_chat_message(user_role, user_id, "user", user_message)

        initial_state = {
            "messages": messages,
            "user_role": user_role,
            "user_info": dict(get_jwt())
        }

        result = graph.invoke(initial_state, {"recursion_limit": AGENT_RECURSION_LIMIT})

        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        if ai_messages and ai_messages[-1].content:
            response_text = ai_messages[-1].content
        else:
            response_text = "I couldn't process your request."

        save_chat_message(user_role, user_id, "assistant", response_text)

        return jsonify({
            "message": response_text,
            "status": "success",
            "role": user_role,
            "pending_actions": get_waiting_actions(user_role, user_id)
        }), 200

    except GraphRecursionError:
        db.session.rollback()
        logger.warning("Chat agent hit the step limit for role %s", user_role)
        return jsonify({
            "message": "That request needed too many steps. Please try breaking it into smaller requests.",
            "status": "failed"
        }), 500

    except Exception:
        db.session.rollback()
        logger.exception("Chat request failed for role %s", user_role)
        return jsonify({
            "message": "Something went wrong while processing your message. Please try again.",
            "status": "failed"
        }), 500


@chatbot_bp.route("/api/chat/history", methods=["GET"])
@jwt_required()
def get_chat_history():
    """The logged-in user's saved conversation, plus deletes still waiting for confirmation."""
    user_role, user_id = get_chat_user()
    if not user_role:
        return jsonify({"message": "Invalid or missing user role", "status": "failed"}), 403

    saved_messages = ChatMessage.query.filter_by(user_id=user_id, user_role=user_role).order_by(ChatMessage.id).all()

    history = [{"role": "assistant", "content": GREETING}]
    for saved in saved_messages:
        history.append({"role": saved.sender, "content": saved.content})

    return jsonify({
        "status": "success",
        "messages": history,
        "pending_actions": get_waiting_actions(user_role, user_id)
    })


@chatbot_bp.route("/api/chat/history", methods=["DELETE"])
@jwt_required()
def clear_chat_history():
    """Start a new conversation: delete the saved messages and cancel waiting deletes."""
    user_role, user_id = get_chat_user()
    if not user_role:
        return jsonify({"message": "Invalid or missing user role", "status": "failed"}), 403

    ChatMessage.query.filter_by(user_id=user_id, user_role=user_role).delete()

    waiting_actions = PendingAction.query.filter_by(user_id=user_id, user_role=user_role, status="waiting").all()
    for action in waiting_actions:
        action.status = "cancelled"

    db.session.commit()

    return jsonify({"message": "Chat history cleared", "status": "success"})


@chatbot_bp.route("/api/chat/confirm", methods=["POST"])
@jwt_required()
def confirm_action():
    """The user clicked Confirm or Cancel on a delete the assistant asked for.

    Body: {"action_id": 5, "approve": true}
    """
    user_role, user_id = get_chat_user()
    if not user_role:
        return jsonify({"message": "Invalid or missing user role", "status": "failed"}), 403

    data = request.get_json() or {}
    action_id = data.get("action_id")
    approve = data.get("approve") is True

    action = PendingAction.query.get(action_id) if action_id else None

    # Only the user the action was made for can confirm it, and only once
    if not action or action.user_id != user_id or action.user_role != user_role:
        return jsonify({"message": "Action not found", "status": "failed"}), 404
    if action.status != "waiting":
        return jsonify({"message": "This action was already handled", "status": "failed"}), 400

    if not approve:
        action.status = "cancelled"
        db.session.commit()
        reply = f"Cancelled. Nothing was deleted ({action.description})."
        save_chat_message(user_role, user_id, "assistant", reply)
        return jsonify({"message": reply, "status": "success", "pending_actions": get_waiting_actions(user_role, user_id)})

    # Find the tool in this user's own tool list (never another role's tools)
    tool_to_run = None
    for tool in ROLE_TOOLS[user_role]:
        if tool.name == action.tool_name:
            tool_to_run = tool

    if not tool_to_run:
        return jsonify({"message": "This action is not allowed for your role", "status": "failed"}), 403

    # Run the tool again with the confirmation flag on. It checks permissions
    # again before deleting, so the delete is still only allowed if it still should be.
    g.confirmed_action = True
    try:
        result = tool_to_run.invoke(json.loads(action.tool_args))
    except Exception:
        db.session.rollback()
        logger.exception("Confirmed chat action %s failed", action.id)
        result = {"message": "The delete failed. Please try again.", "status": "failed"}
    g.confirmed_action = False

    action.status = "done"
    db.session.commit()

    if isinstance(result, dict):
        result_message = result.get("message", "Done")
        result_status = result.get("status", "success")
    else:
        result_message = str(result)
        result_status = "success"

    if result_status in ["failed", "error"]:
        reply = f"Could not delete: {result_message}"
    else:
        reply = f"Done: {action.description}. {result_message}"

    save_chat_message(user_role, user_id, "assistant", reply)

    return jsonify({
        "message": reply,
        "status": result_status,
        "pending_actions": get_waiting_actions(user_role, user_id)
    })
