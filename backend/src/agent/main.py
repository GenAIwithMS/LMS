from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
import operator
import os
from pathlib import Path
from src.agent.tools_list import admin_tools, teacher_tools, student_tools
from src.agent.prompts import admin_system_prompt, teacher_system_prompt, student_system_prompt

# Get the backend directory path (parent of src directory)
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"

# Load environment variables from backend/.env file
load_dotenv(dotenv_path=str(env_path))

model = ChatGroq(model="qwen/qwen3-32b")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_role: str

def get_tools_for_role(user_role: str):
    """Get tools based on user role."""
    if user_role == "admin":
        return admin_tools
    elif user_role == "teacher":
        return teacher_tools
    elif user_role == "student":
        return student_tools
    else:
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
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        messages = [AIMessage(content=system_prompt)] + messages
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def tools_node(state: AgentState, tool_node: ToolNode):
    """Tools node that executes tool calls."""
    return tool_node.invoke(state)

def should_continue(state: AgentState) -> str:
    """Determine whether to continue with tools or end."""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

def create_chatbot_graph(user_role: str):
    tools = get_tools_for_role(user_role)
    system_prompt = get_system_prompt_for_role(user_role)

    tool_node = ToolNode(tools)

    model_with_tools = model.bind_tools(tools)

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", lambda state: agent_node(state, model_with_tools, system_prompt))
    workflow.add_node("tools", lambda state: tools_node(state, tool_node))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()
