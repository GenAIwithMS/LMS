export type UserRole = 'admin' | 'teacher' | 'student';

export interface User {
  id: number;
  name?: string;
  username?: string;
  email?: string;
  role?: UserRole;
  section?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  status: boolean;
  message: string;
  token: string;
}

export interface ApiResponse {
  status: string;
  message?: string;
  [key: string]: any;
}

export interface Student {
  id: number;
  name: string;
  username: string;
  email: string;
  section: string;
  section_id?: number;
}

export interface Teacher {
  id: number;
  name: string;
  username: string;
  email: string;
  subjects?: string[];
}

export interface Section {
  id: number;
  name: string;
  teacher: string;
  teacher_id?: number;
  teacher_name?: string;
}

export interface Course {
  id: number;
  name: string;
  description: string;
  course_code: string;
  teacher: string;
  teacher_id?: number;
}

export interface Subject {
  id: number;
  name: string;
  teacher: string;
  course: string;
  teacher_id?: number;
  course_id?: number;
}

export interface Enrollment {
  id: number;
  student: string;
  student_id?: number;
  course: string;
  course_id?: number;
  enrollment_date: string;
  status: string;
  grade: string;
}

export interface Assignment {
  id: number;
  subject_id?: number;
  title: string;
  description: string;
  due_date: string;
  subject: string;
  teacher: string;
  total_marks: number;
}

export interface Submission {
  id: number;
  assignment: string;
  student?: string;
  submission_text?: string;
  submission_file?: string;
  submitted_at?: string;
  marks_obtained?: number;
  feedback?: string;
}

export interface Attendance {
  id: number;
  subject_id?: number;
  student: string;
  student_id?: number;
  subject: string;
  status: 'present' | 'absent' | 'late';
  mark_at: string;
}

export interface Result {
  id: number;
  subject_id?: number;
  student: string;
  student_id?: number;
  subject: string;
  total_marks: number;
  obtained_marks: number;
  exam_type: string;
  remarks: string;
}

export interface Announcement {
  id: number;
  section_id?: number;
  title: string;
  content: string;
  target_audience: string;
  section: string;
  teacher: string;
  created_at: string;
}

export interface Event {
  id: number;
  title: string;
  description: string;
  event_date: string;
  event_time: string;
  admin: string;
}

