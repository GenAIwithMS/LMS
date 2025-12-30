from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from src.agent.main import create_chatbot_graph, get_tools_for_role
from langchain_core.messages import HumanMessage, AIMessage


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

        with current_app.app_context():
            # user_id = token.get("id")
            graph = create_chatbot_graph(user_role)

            initial_state = {
                "messages": [HumanMessage(content=user_message)],
                "user_role": user_role,
                "user_info": dict(token)
            }

            result = graph.invoke(initial_state)

            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                response_text = ai_messages[-1].content
            else:
                response_text = "I couldn't process your request."

        return jsonify({
            "message": response_text,
            "status": "success",
            "role": user_role
        }), 200

    except Exception as e:
        return jsonify({
            "message": f"An error occurred: {str(e)}",
            "status": "failed"
        }), 500