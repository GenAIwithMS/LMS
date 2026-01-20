from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
import operator
from pathlib import Path
from backend.src.agent.tools_list import admin_tools, teacher_tools, student_tools
from src.agent.prompts import admin_system_prompt, teacher_system_prompt, student_system_prompt

backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"

load_dotenv(dotenv_path=str(env_path))

# Use a faster model or optimize configuration if needed
model = ChatGroq(model="qwen/qwen3-32b")

# Cache tool schemas globally to reduce token usage in multi-turn conversations
_CACHED_TOOL_SCHEMAS = {}

def _build_tool_schemas_cache():
    """Build and cache tool schemas for all roles on initialization."""
    global _CACHED_TOOL_SCHEMAS
    _CACHED_TOOL_SCHEMAS = {
        "admin": model.bind_tools(admin_tools),
        "teacher": model.bind_tools(teacher_tools),
        "student": model.bind_tools(student_tools)
    }

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_role: str
    user_info: dict

def get_tools_for_role(user_role: str):
    """Get tools based on user role."""
    if user_role == "admin":
        return admin_tools
    elif user_role == "teacher":
        return teacher_tools
    elif user_role == "student":
        return student_tools
    return []

def get_system_prompt_for_role(user_role: str):
    """Get system prompt based on user role."""
    return {
        "admin": admin_system_prompt,
        "teacher": teacher_system_prompt,
        "student": student_system_prompt
    }.get(user_role, "You are a helpful assistant.")

def agent_node(state: AgentState, model_with_tools, system_prompt):
    """Agent node that calls the model."""
    messages = state["messages"]
    user_role = state.get("user_role")
    
    context_prompt = f"{system_prompt}\n\nNote: You are logged in as {user_role}. Your identity is automatically used in relevant operations."
    
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        messages = [AIMessage(content=context_prompt)] + messages
    
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Determine whether to continue with tools or end."""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

def create_chatbot_graph(user_role: str):
                         
    """Create a unified agent graph with parallel tool execution and cached tool schemas."""
                         
    # Initialize cache on first call
    if not _CACHED_TOOL_SCHEMAS:
        _build_tool_schemas_cache()
    
    tools = get_tools_for_role(user_role)
    system_prompt = get_system_prompt_for_role(user_role)

    # ToolNode in LangGraph automatically handles parallel execution 
    # if the model returns multiple tool calls in a single message.
    tool_node = ToolNode(tools)
    
    # Use cached tool schemas instead of rebuilding them
    model_with_tools = _CACHED_TOOL_SCHEMAS[user_role]

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", lambda state: agent_node(state, model_with_tools, system_prompt))
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()
