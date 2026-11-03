import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from langgraph.errors import GraphRecursionError
from src.agent.main import create_chatbot_graph
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

# Maximum agent steps per message (each model call or tool round counts as one).
# Stops a confused model from looping and running up API costs.
AGENT_RECURSION_LIMIT = 15

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/api/chat", methods=["POST"])
@jwt_required()
def chat():
    """Chat with the LMS assistant based on user role."""

    token = get_jwt()
    user_role = token.get("role")
    
    if not user_role or user_role not in ["admin", "teacher", "student"]:
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
        conversation_history = data.get("history", [])

        graph = create_chatbot_graph(user_role)

        # Convert conversation history to LangChain messages
        messages = []
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))

        # Add the new user message
        messages.append(HumanMessage(content=user_message))

        initial_state = {
            "messages": messages,
            "user_role": user_role,
            "user_info": dict(token)
        }

        result = graph.invoke(initial_state, {"recursion_limit": AGENT_RECURSION_LIMIT})

        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        if ai_messages and ai_messages[-1].content:
            response_text = ai_messages[-1].content
        else:
            response_text = "I couldn't process your request."

        return jsonify({
            "message": response_text,
            "status": "success",
            "role": user_role
        }), 200

    except GraphRecursionError:
        logger.warning("Chat agent hit the step limit for role %s", user_role)
        return jsonify({
            "message": "That request needed too many steps. Please try breaking it into smaller requests.",
            "status": "failed"
        }), 500

    except Exception:
        logger.exception("Chat request failed for role %s", user_role)
        return jsonify({
            "message": "Something went wrong while processing your message. Please try again.",
            "status": "failed"
        }), 500