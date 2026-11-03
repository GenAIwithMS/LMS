import operator
import os
from pathlib import Path
from typing import TypedDict, Annotated, Sequence

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from src.agent.tools_list import admin_tools, teacher_tools, student_tools
from src.agent.prompts import admin_system_prompt, teacher_system_prompt, student_system_prompt

backend_dir = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=str(backend_dir / ".env"))

# Model settings come from .env so the model can be switched without code changes.
# reasoning_format="hidden" stops reasoning models such as Qwen3 from putting their
# <think>...</think> text into the reply. Set CHAT_REASONING_FORMAT to an empty
# value when using a non-reasoning model.
chat_model_name = os.getenv("CHAT_MODEL", "qwen/qwen3-32b")
reasoning_format = os.getenv("CHAT_REASONING_FORMAT", "hidden")

if reasoning_format:
    model = ChatGroq(model=chat_model_name, temperature=0, max_retries=2, timeout=60, reasoning_format=reasoning_format)
else:
    model = ChatGroq(model=chat_model_name, temperature=0, max_retries=2, timeout=60)

ROLE_TOOLS = {
    "admin": admin_tools,
    "teacher": teacher_tools,
    "student": student_tools,
}

ROLE_PROMPTS = {
    "admin": admin_system_prompt,
    "teacher": teacher_system_prompt,
    "student": student_system_prompt,
}


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_role: str
    user_info: dict


def agent_node(state: AgentState, model_with_tools, system_prompt):
    """Agent node that calls the model."""
    user_role = state.get("user_role")

    context_prompt = f"{system_prompt}\n\nNote: You are logged in as {user_role}. Your identity is automatically used in relevant operations."

    # Send the system prompt on every model call (first turn, follow-up turns,
    # and after tool calls). It is not stored in state, so it never piles up.
    messages = [SystemMessage(content=context_prompt)] + list(state["messages"])

    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Determine whether to continue with tools or end."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def _build_graph(user_role: str):
    tools = ROLE_TOOLS[user_role]
    system_prompt = ROLE_PROMPTS[user_role]
    model_with_tools = model.bind_tools(tools)

    # handle_tool_errors=True: if a tool raises, the model gets the error as a
    # tool message and can explain it, instead of the whole request failing.
    tool_node = ToolNode(tools, handle_tool_errors=True)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", lambda state: agent_node(state, model_with_tools, system_prompt))
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Each role's graph is built once and reused, instead of on every request.
compiled_graphs = {}


def create_chatbot_graph(user_role: str):
    """Return the compiled agent graph for a role, building it on first use."""
    if user_role not in ROLE_TOOLS:
        raise ValueError(f"Unknown role: {user_role}")
    if user_role not in compiled_graphs:
        compiled_graphs[user_role] = _build_graph(user_role)
    return compiled_graphs[user_role]
