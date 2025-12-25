# LMS Chatbot API

## Overview
The LMS Chatbot API provides an AI-powered assistant that helps users interact with the Learning Management System based on their role (admin, teacher, or student).

## Endpoint

### POST /api/chat

Chat with the LMS assistant using natural language.

**Authentication:** Required (JWT Bearer token)

**Request Body:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "message": "Assistant response",
  "status": "success",
  "role": "admin|teacher|student"
}
```

## Role-Based Access

### Admin Tools
- Full system management (students, teachers, courses, sections, subjects, enrollments, events)
- Assignment and submission management
- Attendance and result management
- Announcement management

### Teacher Tools
- Announcement management
- Assignment creation and management
- Attendance marking
- Result management
- Student information viewing
- Assignment submission review

### Student Tools
- Assignment submission
- View personal submissions, attendance, and results
- Read announcements

## Usage Examples

### As an Admin
```
User: "Add a new student named John Doe"
Assistant: [Creates student using add_student tool]

User: "Show me all courses"
Assistant: [Lists all courses using get_courses tool]
```

### As a Teacher
```
User: "Create an assignment for Math class"
Assistant: [Creates assignment using create_assignment tool]

User: "Mark attendance for student ID 123"
Assistant: [Marks attendance using mark_attendance tool]
```

### As a Student
```
User: "Submit my homework"
Assistant: [Guides through assignment submission process]

User: "What assignments are due?"
Assistant: [Shows student's assignments]
```

## Error Responses

```json
{
  "message": "Error description",
  "status": "failed"
}
```

Common errors:
- 400: Invalid request data
- 403: Insufficient permissions or invalid role
- 500: Internal server error

## Testing

Use the provided `test_chatbot.py` script to test the API:

```bash
python test_chatbot.py
```

Make sure to:
1. Start the Flask server: `python app.py`
2. Get a valid JWT token by logging in
3. Update the JWT_TOKEN in the test script
4. Run the test

## Security

- All requests require valid JWT authentication
- User role is extracted from JWT token
- Tools are filtered based on user permissions
- Database operations run within Flask app context