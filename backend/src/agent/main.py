from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
import operator
from pathlib import Path
from src.agent.tools_list import admin_tools, teacher_tools, student_tools
from src.agent.prompts import admin_system_prompt, teacher_system_prompt, student_system_prompt

backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"

load_dotenv(dotenv_path=str(env_path))

model = ChatGroq(model="qwen/qwen3-32b")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_role: str
    user_info: dict

def get_tools_for_role(user_role: str):
    """Get tools based on user role, with optional context injection."""
    if user_role == "admin":
        tools = admin_tools
    elif user_role == "teacher":
        tools = teacher_tools
    elif user_role == "student":
        tools = student_tools
    else:
        return []

    
    return tools

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
    
    # Build context-aware system prompt  
    context_prompt = f"{system_prompt}\n\nNote: You are logged in as {user_role}. Your identity is automatically used in relevant operations."
    
    # Ensure system prompt is present at the beginning
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        messages = [AIMessage(content=context_prompt)] + messages
    
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
    """Create a unified agent graph with all role-based tools."""
    # Get context-aware tools if user_id is provided
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
