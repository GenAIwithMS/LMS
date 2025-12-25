# LMS Agentic Chatbot

A role-based AI chatbot for the Learning Management System (LMS) built with LangGraph and LangChain.

## Features

- **Role-Based Access**: Different tools available based on user role (Admin, Teacher, Student)
- **LangGraph Integration**: State management and tool calling with LangGraph
- **Database Integration**: Full access to LMS database operations
- **Secure Tool Access**: Users only see tools appropriate to their permissions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GROQ_API_KEY=your_groq_api_key
```

3. Ensure database is configured (same as Flask app)

## Running the Chatbot

From the project root directory:

```bash
python run_agent.py
```

Or directly:

```bash
python -m src.agent.main
```

## User Roles

### Admin
- Full system management
- Manage students, teachers, courses, sections, subjects
- Handle enrollments, events, assignments, attendance, results
- Create/manage announcements

### Teacher
- Create and manage announcements
- Handle assignments and submissions
- Mark and view attendance
- Manage student results
- View student information

### Student
- Submit assignments
- View personal submissions and attendance
- Access results and announcements

## Architecture

- **tools.py**: LangChain tools wrapping LMS service functions
- **main.py**: LangGraph chatbot with role-based tool access
- **run_agent.py**: Runner script with Flask app context

## Integration

To integrate with your Flask app's authentication:

1. Extract user role from JWT token
2. Pass role to `create_chatbot_graph(user_role)`
3. Use the graph in your chat endpoints

The chatbot maintains the same security model as your route-based access control.