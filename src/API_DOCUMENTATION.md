# API Documentation

# This document provides a concise reference for the backend API endpoints and how the frontend should integrate with them.

Base URL: `/` (API paths are shown below)

Authentication
- Protected endpoints require a JWT in the `Authorization` header: `Authorization: Bearer <token>`.
- The token contains a `role` claim with one of `admin`, `teacher`, or `student`.

Common response pattern
- Many endpoints return JSON with keys such as `{ "status": <bool|str>, "message": "...", ... }`.

### Login
- **URL**: `/api/login`
- **Method**: `POST`
- **Body**:
  ```json
  { "email": "user@example.com", "password": "password" }
  ```
- **Responses**:
  - `200 OK`: `{ "status": true, "message": "Login successful", "token": "<jwt>", "Result": "<user_str>" }`
  - `401 Unauthorized`: Invalid credentials
  - `400 Bad Request`: Validation error

## User Management

### Admin
- **Add Admin**
  - **URL**: `/api/add-admin`
  - **Method**: `POST`
  - **Body**: Form-data (name, email, username, password, image).
  - **Returns**: Result of creation.

- **Get Admin**
  - **URL**: `/api/get_admin`
  - **Method**: `GET`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Params**: `id` (optional)

### Student
- **Add Student**
  - **URL**: `/api/add/student`
  - **Method**: `POST`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Body**: JSON (name, username, section_id, password, email, teacher_id).
  - **Responses**:
    - `201 Created`: Student added.
    - `400 Bad Request`: Validation error.
    - `403 Forbidden`: Non-admin access.

- **Get Student**
  - **URL**: `/api/get/student`
  - **Method**: `GET`
  - **Headers**: `Authorization: Bearer <token>`
  - **Params**: `id` (optional)
  - **Responses**:
    - `200 OK`: Student list or details.
    - `404 Not Found`: Student not found.
    - `403 Forbidden`: Unauthorized access (if listing all).

- **Update Student**
  - **URL**: `/api/update/student`
  - **Method**: `PUT`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Params**: `id`
  - **Body**: JSON (fields to update).
  - **Responses**:
    - `200 OK`: Update successful.
    - `404 Not Found`: Student not found.
    - `403 Forbidden`: Non-admin access.

- **Delete Student**
  - **URL**: `/api/delete/student`
  - **Method**: `DELETE`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Params**: `id`
  - **Responses**:
    - `200 OK`: Deletion successful.
    - `404 Not Found`: Student not found.
    - `403 Forbidden`: Non-admin access.

### Teacher
- **Add Teacher**
  - **URL**: `/api/add-teacher`
  - **Method**: `POST`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Body**: JSON (name, subject, username, email, password_hash, student_id).
  - **Responses**:
    - `201 Created`: Teacher added.

- **Get Teacher**
  - **URL**: `/api/get/teacher`
  - **Method**: `GET`
  - **Headers**: `Authorization: Bearer <token>`
  - **Params**: `id` (optional)
  - **Responses**:
    - `200 OK`: Teacher details.
    - `404 Not Found`: Teacher not found.

- **Update Teacher**
  - **URL**: `/api/update/teacher`
  - **Method**: `PUT`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Params**: `id`
  - **Responses**:
    - `200 OK`: Success.
    - `404 Not Found`: Not found.

- **Delete Teacher**
  - **URL**: `/api/delete_teacher`
  - **Method**: `DELETE`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Params**: `id`
  - **Responses**:
    - `200 OK`: Success.
    - `404 Not Found`: Not found.

## Academic Resources

### Course
- **Add Course**
  - **URL**: `/api/add/course`
  - **Method**: `POST`
  - **Headers**: `Authorization: Bearer <token>` (Admin only)
  - **Body**: JSON (name, description, course_code, teacher_id, etc.).
  - **Responses**: `201 Created`.

- **Get Courses**
  - **URL**: `/api/get/courses`
  - **Method**: `GET`
  - **Params**: `id` (optional)
  - **Responses**: `200 OK`, `404 Not Found`.

- **Update Course**
  - **URL**: `/api/update/course`
  - **Method**: `PUT`
  - **Params**: `id`
  - **Responses**: `200 OK`, `404 Not Found`.

- **Delete Course**
  - **URL**: `/api/delete/course`
  - **Method**: `DELETE`
  - **Params**: `id`
  - **Responses**: `200 OK`, `404 Not Found`.

### Subject
- **Create Subject**: `POST /api/create_subject` (Admin only)
- **Get Subjects**: `GET /api/get_subjects`
- **Update Subject**: `PUT /api/update_subject`
- **Delete Subject**: `DELETE /api/delete_subject`

### Section
- **Add Section**: `POST /api/add_section` (Admin only)
- **Get Section**: `GET /api/get_section`
- **Update Section**: `PUT /api/update/section`
- **Delete Section**: `DELETE /api/delete/section`

## Learning Management

### Assignments
- **Create**: `POST /api/create/assignments` (Teacher only)
- **Get**: `GET /api/get/assignments`
- **Update**: `PUT /api/update/assignments/`
- **Delete**: `DELETE /api/delete/assignments/`

### Submissions
- **Submit**: `POST /api/submit/assignment`
- **Get by Student**: `GET /api/get/submissions/by_student?id=<student_id>`
- **Get by Assignment**: `GET /api/get/submissions/by_assignment?id=<assignment_id>`
- **Update**: `PUT /api/update/submission`
- **Delete**: `DELETE /api/delete/submission`

### Results
- **Create Result**: `POST /api/create/result` (Teacher only)
- **Get Result**: `GET /api/get/result`
- **Update Result**: `PUT /api/update/result`
- **Delete Result**: `DELETE /api/delete/result`

### Attendance
- **Mark Attendance**: `POST /api/attendance` (Teacher only)
- **Get Attendance**: `GET /api/get/attendance` (by `student_id` or `subject_id`)
- **Update Attendance**: `PUT /api/update/attendance`
- **Delete Attendance**: `DELETE /api/delete/attendance`

### Enrollments
- **Enroll Student**: `POST /api/enroll/student` (Admin only)
- **Get Enrollments**: `GET /api/get/enrollments`
- **Update Enrollment**: `PUT /api/update/enrollment`
- **Delete Enrollment**: `DELETE /api/delete/enrollment`

## Communication & Events

### Announcements
- **Create**: `POST /api/create/announcement` (Teacher only)
- **Get**: `GET /api/get/announcements`
- **Update**: `PUT /api/update/announcement`
- **Delete**: `DELETE /api/delete/announcement`

### Events
- **Create**: `POST /api/create/event` (Admin only)
- **Get**: `GET /api/get/events`
- **Update**: `PUT /api/update/event`
- **Delete**: `DELETE /api/delete/event`

### Chatbot
- **Chat**: `POST /api/chat`
  - **Body**: `{"message": "user question"}`
  - **Response**: `{"message": "AI response", ...}`

## General
- **Home**: `GET /`
- **About**: `GET /about`
