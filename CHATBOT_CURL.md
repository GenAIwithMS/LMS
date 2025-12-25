# LMS Chatbot API - Curl Examples

## Authentication
First, get a JWT token by logging in:

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

## Chat with the Assistant

### Admin Example
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message":"Show me all students"}'
```

### Teacher Example
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message":"Create an announcement for my class"}'
```

### Student Example
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message":"Submit my assignment"}'
```

## Response Format

Success response:
```json
{
  "message": "Assistant response here",
  "status": "success",
  "role": "admin"
}
```

Error response:
```json
{
  "message": "Error message",
  "status": "failed"
}
```

## Common Use Cases

### Admin Commands
- "Add a new student"
- "Create a course"
- "Show all teachers"
- "Manage enrollments"

### Teacher Commands
- "Create assignment"
- "Mark attendance"
- "View student submissions"
- "Add results"

### Student Commands
- "View my assignments"
- "Submit homework"
- "Check my grades"
- "View announcements"