# Learning Management System (LMS) API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Login
Obtain a JWT token by logging in with valid credentials.

**Endpoint:** `POST /api/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": true,
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**
- `400`: Validation error
- `401`: Invalid email or password

---

## User Roles

The API supports three user roles:
- **Admin**: Full system access
- **Teacher**: Can create assignments, mark attendance, add results, create announcements
- **Student**: Can view their own data, submit assignments

---

## API Endpoints

### Authentication

#### Protected Route Test
**Endpoint:** `GET /api/protected`

**Authentication:** Required

**Response:**
```json
{
  "id": "1"
}
```

---

### Admin Management

#### Add Admin
**Endpoint:** `POST /api/add/admin`

**Authentication:** Not required (for initial setup)

**Request Body:**
```json
{
  "name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Admin added successfully",
  "status": "success"
}
```

#### Get Admin(s)
**Endpoint:** `GET /api/get/admin`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (optional): Admin ID to retrieve specific admin

**Response (All Admins):**
```json
[
  {
    "id": 1,
    "username": "johndoe"
  }
]
```

---

### Student Management

#### Add Student
**Endpoint:** `POST /api/add/student`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Jane Smith",
  "username": "janesmith",
  "email": "jane@example.com",
  "password": "password123",
  "section_name": "Section A"
}
```

**Response:**
```json
{
  "message": "Student added successfully",
  "status": "success"
}
```

#### Get Student(s)
**Endpoint:** `GET /api/get/student`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Student ID

**Access Control:**
- Admin/Teacher: Can view all students
- Student: Can only view their own data

**Response (Single Student):**
```json
{
  "student": {
    "id": 1,
    "name": "Jane Smith",
    "username": "janesmith",
    "email": "jane@example.com",
    "section": "Section A"
  }
}
```

#### Update Student
**Endpoint:** `PUT /api/update/student`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Student ID

**Request Body:**
```json
{
  "name": "Jane Smith Updated",
  "email": "jane.updated@example.com",
  "section_name": "Section B",
  "password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Student updated successfully",
  "status": "success"
}
```

#### Delete Student
**Endpoint:** `DELETE /api/delete/student`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Student ID

**Response:**
```json
{
  "message": "Student deleted successfully",
  "status": "success"
}
```

---

### Teacher Management

#### Add Teacher
**Endpoint:** `POST /api/add/teacher`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Dr. Smith",
  "username": "drsmith",
  "email": "smith@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "teacher added successfully",
  "status": "success"
}
```

#### Get Teacher(s)
**Endpoint:** `GET /api/get/teacher`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Teacher ID

**Access Control:**
- Admin: Can view all teachers
- Others: Can view specific teacher by ID

**Response (Single Teacher):**
```json
{
  "teacher": {
    "id": 1,
    "name": "Dr. Smith",
    "username": "drsmith",
    "email": "smith@example.com",
    "subjects": ["Mathematics", "Physics"]
  }
}
```

#### Update Teacher
**Endpoint:** `PUT /api/update/teacher`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Teacher ID

**Request Body:**
```json
{
  "name": "Dr. Smith Updated",
  "email": "smith.updated@example.com",
  "password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "teacher updated successfully",
  "status": "success"
}
```

#### Delete Teacher
**Endpoint:** `DELETE /api/delete/teacher`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Teacher ID

**Response:**
```json
{
  "message": "teacher deleted successfully",
  "status": "success"
}
```

---

### Section Management

#### Add Section
**Endpoint:** `POST /api/add/section`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Section A",
  "teacher_name": "Dr. Smith"
}
```

**Response:**
```json
{
  "message": "Section added successfully",
  "status": "success"
}
```

#### Get Section(s)
**Endpoint:** `GET /api/get/section`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Section ID

**Response:**
```json
{
  "section": {
    "id": 1,
    "name": "Section A",
    "teacher": "Dr. Smith"
  }
}
```

#### Update Section
**Endpoint:** `PUT /api/update/section`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Section ID

**Request Body:**
```json
{
  "name": "Section A Updated",
  "teacher_name": "Dr. Johnson"
}
```

**Response:**
```json
{
  "message": "Section updated successfully",
  "status": "success"
}
```

#### Delete Section
**Endpoint:** `DELETE /api/delete/section`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Section ID

**Response:**
```json
{
  "message": "Section deleted successfully",
  "status": "success"
}
```

---

### Course Management

#### Add Course
**Endpoint:** `POST /api/add/course`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Computer Science 101",
  "description": "Introduction to Computer Science",
  "course_code": "CS101",
  "teacher_name": "Dr. Smith",
  "created_at": "2024-01-01"
}
```

**Response:**
```json
{
  "message": "Course added successfully",
  "status": "success"
}
```

#### Get Course(s)
**Endpoint:** `GET /api/get/courses`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Course ID

**Response:**
```json
{
  "course": {
    "id": 1,
    "name": "Computer Science 101",
    "description": "Introduction to Computer Science",
    "course_code": "CS101",
    "teacher": "Dr. Smith"
  }
}
```

#### Update Course
**Endpoint:** `PUT /api/update/course`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Course ID

**Request Body:**
```json
{
  "name": "Computer Science 101 Updated",
  "description": "Updated description",
  "teacher_name": "Dr. Johnson"
}
```

**Response:**
```json
{
  "message": "Course updated successfully",
  "status": "success"
}
```

#### Delete Course
**Endpoint:** `DELETE /api/delete/course`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Course ID

**Response:**
```json
{
  "message": "Course deleted successfully",
  "status": "success"
}
```

---

### Subject Management

#### Create Subject
**Endpoint:** `POST /api/create/subject`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Mathematics",
  "teacher_name": "Dr. Smith",
  "course_name": "Computer Science 101"
}
```

**Response:**
```json
{
  "message": "Subject created successfully",
  "status": "success"
}
```

#### Get Subject(s)
**Endpoint:** `GET /api/get/subjects`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Subject ID

**Response:**
```json
{
  "subject": {
    "id": 1,
    "name": "Mathematics",
    "teacher": "Dr. Smith",
    "course": "Computer Science 101"
  }
}
```

#### Update Subject
**Endpoint:** `PUT /api/update/subject`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Subject ID

**Request Body:**
```json
{
  "name": "Advanced Mathematics",
  "teacher_name": "Dr. Johnson",
  "course_name": "Computer Science 101"
}
```

**Response:**
```json
{
  "message": "Subject updated successfully",
  "status": "success"
}
```

#### Delete Subject
**Endpoint:** `DELETE /api/delete/subject`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Subject ID

**Response:**
```json
{
  "message": "Subject deleted successfully",
  "status": "success"
}
```

---

### Enrollment Management

#### Enroll Student
**Endpoint:** `POST /api/enroll/student`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "student_name": "Jane Smith",
  "course_name": "Computer Science 101",
  "enrollment_date": "2024-01-01",
  "status": "active",
  "grade": "A"
}
```

**Response:**
```json
{
  "message": "Student enrolled successfully",
  "status": "success"
}
```

#### Get Enrollments
**Endpoint:** `GET /api/get/enrollments`

**Authentication:** Required

**Query Parameters:**
- `course_name` (optional): Filter by course name
- `student_name` (optional): Filter by student name
- If no parameters: Returns all enrollments

**Response:**
```json
[
  {
    "id": 1,
    "student": "Jane Smith",
    "course": "Computer Science 101",
    "enrollment_date": "2024-01-01",
    "status": "active",
    "grade": "A"
  }
]
```

#### Update Enrollment
**Endpoint:** `PUT /api/update/enrollment`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Enrollment ID

**Request Body:**
```json
{
  "status": "completed",
  "grade": "A+"
}
```

**Response:**
```json
{
  "message": "Enrollment updated successfully",
  "status": "success"
}
```

#### Delete Enrollment
**Endpoint:** `DELETE /api/delete/enrollment`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Enrollment ID

**Response:**
```json
{
  "message": "Enrollment deleted successfully",
  "status": "success"
}
```

---

### Assignment Management

#### Create Assignment
**Endpoint:** `POST /api/create/assignments`

**Authentication:** Required (Teacher only)

**Request Body:**
```json
{
  "title": "Assignment 1",
  "description": "Complete the following exercises",
  "due_date": "2024-12-31",
  "subject_name": "Mathematics",
  "total_marks": 100
}
```

**Response:**
```json
{
  "message": "Assignment created successfully",
  "status": "success"
}
```

#### Get Assignment(s)
**Endpoint:** `GET /api/get/assignments`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Assignment ID

**Response:**
```json
{
  "assignment": {
    "id": 1,
    "title": "Assignment 1",
    "description": "Complete the following exercises",
    "due_date": "2024-12-31",
    "subject": "Mathematics",
    "teacher": "Dr. Smith",
    "total_marks": 100
  }
}
```

#### Update Assignment
**Endpoint:** `PUT /api/update/assignments/`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Assignment ID

**Request Body:**
```json
{
  "title": "Assignment 1 Updated",
  "description": "Updated description",
  "due_date": "2025-01-15",
  "subject_name": "Mathematics",
  "total_marks": 120
}
```

**Response:**
```json
{
  "message": "Assignment updated successfully",
  "status": "success"
}
```

#### Delete Assignment
**Endpoint:** `DELETE /api/delete/assignments/`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Assignment ID

**Response:**
```json
{
  "message": "Assignment deleted successfully",
  "status": "success"
}
```

---

### Assignment Submission

#### Submit Assignment
**Endpoint:** `POST /api/submit/assignment`

**Authentication:** Required (Student only)

**Request:** Form-data (multipart/form-data)

**Form Fields:**
- `assignment_id` (required): Assignment ID
- `submission_text` (optional): Text submission
- `submission_file` (optional): File upload
- `submitted_at` (optional): Submission date
- `feedback` (optional): Feedback from teacher

**Response:**
```json
{
  "message": "Assignment submitted successfully",
  "status": "success"
}
```

#### Get Submissions by Student
**Endpoint:** `GET /api/get/submissions/by/student`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Student ID (defaults to current user for students)

**Access Control:**
- Students: Can only view their own submissions
- Teachers/Admins: Can view any student's submissions

**Response:**
```json
[
  {
    "id": 1,
    "assignment": "Assignment 1",
    "submission_text": "My submission",
    "submitted_at": "2024-01-15",
    "marks_obtained": 85,
    "feedback": "Good work"
  }
]
```

#### Get Submissions by Assignment
**Endpoint:** `GET /api/get/submissions/by/assignment`

**Authentication:** Required

**Query Parameters:**
- `id` (required): Assignment ID

**Response:**
```json
[
  {
    "id": 1,
    "student": "Jane Smith",
    "submission_text": "My submission",
    "submitted_at": "2024-01-15",
    "marks_obtained": 85,
    "feedback": "Good work"
  }
]
```

#### Update Submission
**Endpoint:** `PUT /api/update/submission`

**Authentication:** Required

**Query Parameters:**
- `id` (required): Submission ID

**Request Body:**
```json
{
  "submission_text": "Updated submission",
  "marks_obtained": 90,
  "feedback": "Excellent work"
}
```

**Response:**
```json
{
  "message": "Submission updated successfully",
  "status": "success"
}
```

#### Delete Submission
**Endpoint:** `DELETE /api/delete/submission`

**Authentication:** Required

**Query Parameters:**
- `id` (required): Submission ID

**Response:**
```json
{
  "message": "Submission deleted successfully",
  "status": "success"
}
```

---

### Attendance Management

#### Mark Attendance
**Endpoint:** `POST /api/attendance`

**Authentication:** Required (Teacher only)

**Request Body:**
```json
{
  "student_name": "Jane Smith",
  "subject_name": "Mathematics",
  "status": "present"
}
```

**Status Values:** `present`, `absent`, `late`

**Response:**
```json
{
  "message": "Attendance marked successfully",
  "status": "success"
}
```

#### Get Attendance
**Endpoint:** `GET /api/get/attendance`

**Authentication:** Required

**Query Parameters:**
- `student_name` (optional): Filter by student name
- `subject_name` (optional): Filter by subject name
- If no parameters: Returns all attendance records

**Response:**
```json
[
  {
    "id": 1,
    "student": "Jane Smith",
    "subject": "Mathematics",
    "status": "present",
    "mark_at": "2024-01-15T10:00:00"
  }
]
```

#### Update Attendance
**Endpoint:** `PUT /api/update/attendance`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Attendance ID

**Request Body:**
```json
{
  "status": "late",
  "student_name": "Jane Smith",
  "subject_name": "Mathematics"
}
```

**Response:**
```json
{
  "message": "Attendance updated successfully",
  "status": "success"
}
```

#### Delete Attendance
**Endpoint:** `DELETE /api/delete/attendance`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Attendance ID
- OR
- `student_name` (required): Student name
- `subject_name` (required): Subject name

**Response:**
```json
{
  "message": "Attendance deleted successfully",
  "status": "success"
}
```

---

### Result Management

#### Create Result
**Endpoint:** `POST /api/create/result`

**Authentication:** Required (Teacher only)

**Request Body:**
```json
{
  "student_name": "Jane Smith",
  "subject_name": "Mathematics",
  "total_marks": 100,
  "obtained_marks": 85,
  "exam_type": "midterm",
  "remarks": "Good performance"
}
```

**Response:**
```json
{
  "message": "Result created successfully",
  "status": "success"
}
```

#### Get Result(s)
**Endpoint:** `GET /api/get/result`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Result ID

**Access Control:**
- Admin/Teacher: Can view all results
- Student: Can view their own results

**Response:**
```json
{
  "result": {
    "id": 1,
    "student": "Jane Smith",
    "subject": "Mathematics",
    "total_marks": 100,
    "obtained_marks": 85,
    "exam_type": "midterm",
    "remarks": "Good performance"
  }
}
```

#### Update Result
**Endpoint:** `PUT /api/update/result`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Result ID

**Request Body:**
```json
{
  "obtained_marks": 90,
  "remarks": "Excellent performance"
}
```

**Response:**
```json
{
  "message": "Result updated successfully",
  "status": "success"
}
```

#### Delete Result
**Endpoint:** `DELETE /api/delete/result`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Result ID

**Response:**
```json
{
  "message": "Result deleted successfully",
  "status": "success"
}
```

---

### Announcement Management

#### Create Announcement
**Endpoint:** `POST /api/create/announcement`

**Authentication:** Required (Teacher only)

**Request Body:**
```json
{
  "title": "Important Notice",
  "content": "Classes will be cancelled tomorrow",
  "target_audience": "all",
  "section_name": "Section A"
}
```

**Response:**
```json
{
  "message": "Announcement created successfully",
  "status": "success"
}
```

#### Get Announcement(s)
**Endpoint:** `GET /api/get/announcements`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Announcement ID

**Response:**
```json
{
  "announcement": {
    "id": 1,
    "title": "Important Notice",
    "content": "Classes will be cancelled tomorrow",
    "target_audience": "all",
    "section": "Section A",
    "teacher": "Dr. Smith",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

#### Update Announcement
**Endpoint:** `PUT /api/update/announcement`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Announcement ID

**Request Body:**
```json
{
  "title": "Updated Notice",
  "content": "Updated content",
  "section_name": "Section B"
}
```

**Response:**
```json
{
  "message": "Announcement updated successfully",
  "status": "success"
}
```

#### Delete Announcement
**Endpoint:** `DELETE /api/delete/announcement`

**Authentication:** Required (Teacher only)

**Query Parameters:**
- `id` (required): Announcement ID

**Response:**
```json
{
  "message": "Announcement deleted successfully",
  "status": "success"
}
```

---

### Event Management

#### Create Event
**Endpoint:** `POST /api/create/event`

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "title": "Annual Sports Day",
  "description": "School sports day event",
  "event_date": "2024-03-15",
  "event_time": "09:00:00"
}
```

**Response:**
```json
{
  "message": "Event created successfully",
  "status": "success"
}
```

#### Get Event(s)
**Endpoint:** `GET /api/get/events`

**Authentication:** Required

**Query Parameters:**
- `id` (optional): Event ID

**Response:**
```json
{
  "event": {
    "id": 1,
    "title": "Annual Sports Day",
    "description": "School sports day event",
    "event_date": "2024-03-15",
    "event_time": "09:00:00",
    "admin": "John Doe"
  }
}
```

#### Update Event
**Endpoint:** `PUT /api/update/event`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Event ID

**Request Body:**
```json
{
  "title": "Updated Event Title",
  "description": "Updated description",
  "event_date": "2024-03-20"
}
```

**Response:**
```json
{
  "message": "Event updated successfully",
  "status": "success"
}
```

#### Delete Event
**Endpoint:** `DELETE /api/delete/event`

**Authentication:** Required (Admin only)

**Query Parameters:**
- `id` (required): Event ID

**Response:**
```json
{
  "message": "Event deleted successfully",
  "status": "success"
}
```

---

### Chatbot

#### Chat with LMS Assistant
**Endpoint:** `POST /api/chat`

**Authentication:** Required

**Request Body:**
```json
{
  "message": "What assignments do I have?"
}
```

**Response:**
```json
{
  "message": "You have 3 assignments due this week...",
  "status": "success",
  "role": "student"
}
```

**Note:** The chatbot provides role-specific assistance based on the authenticated user's role.

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "message": "Validation error details",
  "status": "failed"
}
```

### 401 Unauthorized
```json
{
  "message": "Invalid credentials",
  "status": "failed"
}
```

### 403 Forbidden
```json
{
  "message": "You don't have permission to access this resource",
  "status": "failed"
}
```

### 404 Not Found
```json
{
  "message": "Resource not found",
  "status": "failed"
}
```

### 500 Internal Server Error
```json
{
  "message": "An error occurred: <error details>",
  "status": "failed"
}
```

---

## Environment Variables

The application supports the following environment variables:

- `JWT_SECRET_KEY`: Secret key for JWT token generation (default: "supersecretkey")
- `DATABASE_URI`: Database connection string (default: "mysql+pymysql://root:@localhost/llm_LMS")
- `FLASK_DEBUG`: Enable/disable debug mode (default: "True")
- `PORT`: Port number for the application (default: 5000)

Create a `.env` file in the root directory to set these variables.

---

## Notes

1. All dates should be in ISO format: `YYYY-MM-DD`
2. All times should be in format: `HH:MM:SS`
3. File uploads for assignment submissions should use `multipart/form-data`
4. JWT tokens should be included in the `Authorization` header as `Bearer <token>`
5. Query parameters are used for filtering and specifying IDs in GET requests
6. Request bodies are used for POST and PUT requests
7. DELETE requests typically use query parameters for IDs

---

## Rate Limiting

Currently, there is no rate limiting implemented. Consider implementing rate limiting for production use.

---

## Security Considerations

1. Always use HTTPS in production
2. Store JWT_SECRET_KEY securely
3. Use strong passwords
4. Implement rate limiting
5. Validate and sanitize all inputs
6. Use parameterized queries (already implemented via SQLAlchemy)

---

## Support

For issues or questions, please contact the development team.

