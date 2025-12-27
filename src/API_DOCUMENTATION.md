# LMS API Documentation

This document provides comprehensive documentation for the Learning Management System (LMS) API endpoints.

## Base Information

- **Base URL**: `/`
- **Authentication**: JWT Bearer tokens required for protected endpoints
- **Headers**: `Authorization: Bearer <token>`
- **Token Claims**: Contains `role` (admin/teacher/student) and `id`
- **Content-Type**: `application/json` for request bodies

## Common Response Patterns

- **Success**: `{ "message": "Success message", "status": "success" }`
- **Error**: `{ "message": "Error message", "status": "error" }`
- **Data Response**: `{ "data": {...}, "status": "success" }`
- **Validation Error**: `{ "messages": {...} }` (400 status)

## Authentication

### Login
- **URL**: `/api/login`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Responses**:
  - `200 OK`: `{ "status": true, "message": "Login successful", "token": "<jwt>", "Result": "<user_info>" }`
  - `401 Unauthorized`: `{ "message": "Invalid credentials" }`
  - `400 Bad Request`: Validation errors

## User Management

### Admin

#### Add Admin
- **URL**: `/api/add-admin`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**: Form-data (name, email, username, password, image)
- **Responses**:
  - `201 Created`: Admin created
  - `403 Forbidden`: Non-admin access

#### Get Admin
- **URL**: `/api/get_admin`
- **Method**: `GET`
- **Auth**: Admin only
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Admin data
  - `404 Not Found`: Admin not found

### Students

#### Add Student
- **URL**: `/api/add/student`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "name": "John Doe",
    "username": "johndoe",
    "section_name": "Grade 10A",
    "email": "john@example.com",
    "password": "password"
  }
  ```
- **Responses**:
  - `201 Created`: Student created
  - `400 Bad Request`: Validation error or section/teacher not found
  - `403 Forbidden`: Non-admin access

#### Get Students
- **URL**: `/api/get/students`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional, for specific student)
- **Responses**:
  - `200 OK`: Student list or single student with section_name and teacher_name
  - `404 Not Found`: Student not found

#### Update Student
- **URL**: `/api/update/student`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update (name, username, section_name, email)
- **Responses**:
  - `200 OK`: Update successful
  - `400 Bad Request`: Validation error or section not found
  - `404 Not Found`: Student not found
  - `403 Forbidden`: Non-admin access

#### Delete Student
- **URL**: `/api/delete/student`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Student not found
  - `403 Forbidden`: Non-admin access

### Teachers

#### Add Teacher
- **URL**: `/api/add-teacher`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "name": "Dr. Smith",
    "subject_name": "Mathematics",
    "username": "drsmith",
    "email": "smith@example.com",
    "password_hash": "hashed_password"
  }
  ```
- **Responses**:
  - `201 Created`: Teacher created
  - `400 Bad Request`: Validation error or subject not found
  - `403 Forbidden`: Non-admin access

#### Get Teachers
- **URL**: `/api/get/teachers`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Teacher list or single teacher with subject_name
  - `404 Not Found`: Teacher not found

#### Update Teacher
- **URL**: `/api/update/teacher`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Teacher not found
  - `403 Forbidden`: Non-admin access

#### Delete Teacher
- **URL**: `/api/delete_teacher`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Teacher not found
  - `403 Forbidden`: Non-admin access

## Academic Resources

### Courses

#### Add Course
- **URL**: `/api/add/course`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "name": "Advanced Mathematics",
    "description": "Calculus and Algebra",
    "course_code": "MATH301",
    "teacher_name": "Dr. Smith"
  }
  ```
- **Responses**:
  - `201 Created`: Course created
  - `400 Bad Request`: Validation error or teacher not found
  - `403 Forbidden`: Non-admin access

#### Get Courses
- **URL**: `/api/get/courses`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Course list or single course with teacher_name
  - `404 Not Found`: Course not found

#### Update Course
- **URL**: `/api/update/course`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update (can include teacher_name)
- **Responses**:
  - `200 OK`: Update successful
  - `400 Bad Request`: Validation error or teacher not found
  - `404 Not Found`: Course not found
  - `403 Forbidden`: Non-admin access

#### Delete Course
- **URL**: `/api/delete/course`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful (cascades to related records)
  - `404 Not Found`: Course not found
  - `403 Forbidden`: Non-admin access

### Subjects

#### Add Subject
- **URL**: `/api/create_subject`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "name": "Calculus",
    "teacher_name": "Dr. Smith",
    "course_name": "Advanced Mathematics"
  }
  ```
- **Responses**:
  - `201 Created`: Subject created
  - `400 Bad Request`: Validation error or teacher/course not found
  - `403 Forbidden`: Non-admin access

#### Get Subjects
- **URL**: `/api/get_subjects`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Subject list or single subject with teacher_name and course_name
  - `404 Not Found`: Subject not found

#### Update Subject
- **URL**: `/api/update_subject`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Subject not found
  - `403 Forbidden`: Non-admin access

#### Delete Subject
- **URL**: `/api/delete_subject`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Subject not found
  - `403 Forbidden`: Non-admin access

### Sections

#### Add Section
- **URL**: `/api/add_section`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "name": "Grade 10A",
    "teacher_name": "Dr. Smith"
  }
  ```
- **Responses**:
  - `201 Created`: Section created
  - `400 Bad Request`: Validation error or teacher not found
  - `403 Forbidden`: Non-admin access

#### Get Sections
- **URL**: `/api/get_sections`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Section list or single section with teacher_name
  - `404 Not Found`: Section not found

#### Update Section
- **URL**: `/api/update/section`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Section not found
  - `403 Forbidden`: Non-admin access

#### Delete Section
- **URL**: `/api/delete/section`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Section not found
  - `403 Forbidden`: Non-admin access

## Learning Management

### Assignments

#### Create Assignment
- **URL**: `/api/create/assignments`
- **Method**: `POST`
- **Auth**: Teacher only
- **Body**:
  ```json
  {
    "title": "Homework 1",
    "description": "Complete exercises 1-10",
    "subject_name": "Mathematics",
    "due_date": "2024-12-31",
    "total_marks": 100.00
  }
  ```
- **Responses**:
  - `201 Created`: Assignment created
  - `400 Bad Request`: Validation error or subject not found
  - `403 Forbidden`: Non-teacher access

#### Get Assignments
- **URL**: `/api/get/assignments`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Assignment list or single assignment with subject_name and teacher_name
  - `404 Not Found`: Assignment not found

#### Update Assignment
- **URL**: `/api/update/assignments/`
- **Method**: `PUT`
- **Auth**: Teacher only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Assignment not found
  - `403 Forbidden`: Non-teacher access

#### Delete Assignment
- **URL**: `/api/delete/assignments/`
- **Method**: `DELETE`
- **Auth**: Teacher only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Assignment not found
  - `403 Forbidden`: Non-teacher access

### Assignment Submissions

#### Submit Assignment
- **URL**: `/api/submit/assignment`
- **Method**: `POST`
- **Auth**: Student only
- **Body**:
  ```json
  {
    "assignment_id": 1,
    "submission_text": "My solution...",
    "submission_file": "path/to/file"
  }
  ```
- **Responses**:
  - `201 Created`: Submission created
  - `400 Bad Request`: Validation error
  - `403 Forbidden`: Non-student access

#### Get Submissions by Student
- **URL**: `/api/get/submissions/by_student`
- **Method**: `GET`
- **Auth**: Required
- **Responses**:
  - `200 OK`: Submission list for current student

#### Get Submissions by Assignment
- **URL**: `/api/get/submissions/by_assignment`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (assignment ID)
- **Responses**:
  - `200 OK`: Submission list for assignment
  - `404 Not Found`: Assignment not found

#### Update Submission
- **URL**: `/api/update/submission`
- **Method**: `PUT`
- **Auth**: Required
- **Query Params**: `id` (submission ID)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Submission not found

#### Delete Submission
- **URL**: `/api/delete/submission`
- **Method**: `DELETE`
- **Auth**: Required
- **Query Params**: `id` (submission ID)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Submission not found

### Results

#### Create Result
- **URL**: `/api/create/result`
- **Method**: `POST`
- **Auth**: Teacher only
- **Body**:
  ```json
  {
    "student_name": "John Doe",
    "subject_name": "Mathematics",
    "total_marks": 100.0,
    "obtained_marks": 85.0,
    "exam_type": "midterm",
    "remarks": "Good work"
  }
  ```
- **Responses**:
  - `201 Created`: Result created
  - `400 Bad Request`: Validation error or student/subject not found
  - `403 Forbidden`: Non-teacher access

#### Get Results
- **URL**: `/api/get/results`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `id` (optional)
- **Responses**:
  - `200 OK`: Result list or single result with student_name and subject_name
  - `404 Not Found`: Result not found

#### Update Result
- **URL**: `/api/update/result`
- **Method**: `PUT`
- **Auth**: Teacher only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Result not found
  - `403 Forbidden`: Non-teacher access

#### Delete Result
- **URL**: `/api/delete/result`
- **Method**: `DELETE`
- **Auth**: Teacher only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Result not found
  - `403 Forbidden`: Non-teacher access

### Attendance

#### Mark Attendance
- **URL**: `/api/attendance`
- **Method**: `POST`
- **Auth**: Teacher only
- **Body**:
  ```json
  {
    "student_name": "John Doe",
    "subject_name": "Mathematics",
    "status": "present"
  }
  ```
- **Responses**:
  - `201 Created`: Attendance marked
  - `400 Bad Request`: Validation error or student/subject not found
  - `403 Forbidden`: Non-teacher access

#### Get Attendance
- **URL**: `/api/get/attendance`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `student_name` or `subject_name` (optional)
- **Responses**:
  - `200 OK`: Attendance records with student_name and subject_name
  - `400 Bad Request`: Student or subject not found

#### Update Attendance
- **URL**: `/api/update/attendance`
- **Method**: `PUT`
- **Auth**: Teacher only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update (status, or student_name/subject_name)
- **Responses**:
  - `200 OK`: Update successful
  - `400 Bad Request`: Validation error
  - `404 Not Found`: Attendance not found
  - `403 Forbidden`: Non-teacher access

#### Delete Attendance
- **URL**: `/api/delete/attendance`
- **Method**: `DELETE`
- **Auth**: Teacher only
- **Body**:
  ```json
  {
    "student_name": "John Doe",
    "subject_name": "Mathematics"
  }
  ```
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Attendance not found
  - `403 Forbidden`: Non-teacher access

### Enrollments

#### Enroll Student
- **URL**: `/api/enroll/student`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "student_name": "John Doe",
    "course_name": "Mathematics",
    "enrollment_date": "2024-01-01",
    "status": "active",
    "grade": "A"
  }
  ```
- **Responses**:
  - `201 Created`: Enrollment created
  - `400 Bad Request`: Validation error or student/course not found
  - `403 Forbidden`: Non-admin access

#### Get Enrollments
- **URL**: `/api/get/enrollments`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `student_name` or `course_name` (optional)
- **Responses**:
  - `200 OK`: Enrollment list with student_name and course_name
  - `400 Bad Request`: Student or course not found

#### Update Enrollment
- **URL**: `/api/update/enrollment`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Enrollment not found
  - `403 Forbidden`: Non-admin access

#### Delete Enrollment
- **URL**: `/api/delete/enrollment`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Enrollment not found
  - `403 Forbidden`: Non-admin access

## Communication & Events

### Announcements

#### Create Announcement
- **URL**: `/api/create/announcement`
- **Method**: `POST`
- **Auth**: Teacher only
- **Body**:
  ```json
  {
    "title": "Exam Reminder",
    "content": "Don't forget the math exam tomorrow",
    "section_name": "Grade 10A",
    "target_audience": "all"
  }
  ```
- **Responses**:
  - `201 Created`: Announcement created
  - `400 Bad Request`: Validation error or section not found
  - `403 Forbidden`: Non-teacher access

#### Get Announcements
- **URL**: `/api/get/announcements`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `announcement_id` (optional)
- **Responses**:
  - `200 OK`: Announcement list or single announcement with section_name
  - `404 Not Found`: Announcement not found

#### Update Announcement
- **URL**: `/api/update/announcement`
- **Method**: `PUT`
- **Auth**: Teacher only
- **Query Params**: `id` (required)
- **Body**: JSON with fields to update (can include section_name)
- **Responses**:
  - `200 OK`: Update successful
  - `400 Bad Request`: Section not found
  - `404 Not Found`: Announcement not found
  - `403 Forbidden`: Non-teacher access

#### Delete Announcement
- **URL**: `/api/delete/announcement`
- **Method**: `DELETE`
- **Auth**: Teacher only
- **Query Params**: `announcement_id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Announcement not found
  - `403 Forbidden`: Non-teacher access

### Events

#### Create Event
- **URL**: `/api/create/event`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "title": "School Fair",
    "description": "Annual school fair",
    "event_date": "2024-12-25",
    "event_time": "10:00:00"
  }
  ```
- **Responses**:
  - `201 Created`: Event created
  - `403 Forbidden`: Non-admin access

#### Get Events
- **URL**: `/api/get/events`
- **Method**: `GET`
- **Auth**: Required
- **Query Params**: `event_id` (optional)
- **Responses**:
  - `200 OK`: Event list or single event
  - `404 Not Found`: Event not found

#### Update Event
- **URL**: `/api/update/event`
- **Method**: `PUT`
- **Auth**: Admin only
- **Query Params**: `event_id` (required)
- **Body**: JSON with fields to update
- **Responses**:
  - `200 OK`: Update successful
  - `404 Not Found`: Event not found
  - `403 Forbidden`: Non-admin access

#### Delete Event
- **URL**: `/api/delete/event`
- **Method**: `DELETE`
- **Auth**: Admin only
- **Query Params**: `event_id` (required)
- **Responses**:
  - `200 OK`: Deletion successful
  - `404 Not Found`: Event not found
  - `403 Forbidden`: Non-admin access

### Chatbot

#### Chat
- **URL**: `/api/chat`
- **Method**: `POST`
- **Auth**: Required
- **Body**:
  ```json
  {
    "message": "What assignments do I have?"
  }
  ```
- **Responses**:
  - `200 OK`: `{ "message": "AI response", "data": {...} }`

## General

### Home
- **URL**: `/`
- **Method**: `GET`
- **Responses**: `200 OK`: Welcome message

### About
- **URL**: `/about`
- **Method**: `GET`
- **Responses**: `200 OK`: About information
