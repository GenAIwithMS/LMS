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
  roll_number?: string | null;
  admission_number?: string | null;
  guardian_name?: string | null;
  guardian_phone?: string | null;
  date_of_birth?: string | null;
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
  full_name?: string;      // "Class 5 - A"
  class_id?: number | null;
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


// ---------------- School structure (Classes 1-10)

export interface ClassSection {
  id: number;
  name: string;            // "A"
  full_name: string;       // "Class 5 - A"
  class_id: number | null;
  incharge_id: number | null;
  incharge_name: string | null;
  student_count: number;
}

export interface SchoolClassSummary {
  id: number;
  name: string;            // "Class 5"
  level: number;
  sections: ClassSection[];
  subject_count: number;
}

export interface ClassSubject {
  id: number;
  name: string;
  chapter_count: number;
}

export interface SchoolClassDetails {
  id: number;
  name: string;
  level: number;
  sections: ClassSection[];
  subjects: ClassSubject[];
}

export interface SectionSubjectTeacher {
  subject_id: number;
  subject_name: string;
  teacher_id: number | null;
  teacher_name: string | null;
}

export interface SectionDetails extends ClassSection {
  class_name: string | null;
  students: { id: number; name: string; username: string; roll_number: string | null }[];
  subjects: SectionSubjectTeacher[];
}

export interface SyllabusChapter {
  id: number;
  subject_id: number;
  number: number;
  title: string;
  description: string | null;
}

export interface AcademicSession {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
}

export interface TeachingItem {
  section_id: number;
  section_name: string;
  subject_id: number;
  subject_name: string;
  chapter_count: number;
  student_count: number;
}

export interface MyClasses {
  incharge_of: ClassSection[];
  teaching: TeachingItem[];
}

export interface MyClass {
  section_id: number | null;
  section_name: string | null;
  class_name: string | null;
  incharge_name: string | null;
  roll_number: string | null;
  subjects: { subject_id: number; subject_name: string; teacher_name: string | null }[];
}

// ---------------- Teaching

export type AttendanceStatus = 'present' | 'absent' | 'late' | 'leave';

export interface RegisterStudent {
  student_id: number;
  name: string;
  roll_number: string | null;
  status: AttendanceStatus | null;
}

export interface AttendanceRegister {
  section_id: number;
  section_name: string;
  incharge_id: number | null;
  incharge_name: string | null;
  date: string;
  is_marked: boolean;
  marked_count: number;
  students: RegisterStudent[];
}

export interface AttendanceCounts {
  present: number;
  absent: number;
  late: number;
  leave: number;
  total_days: number;
  percentage: number | null;
}

export interface StudentMonthSummary extends AttendanceCounts {
  student_id: number;
  name: string;
  roll_number: string | null;
}

export interface MyDailyAttendance {
  summary: AttendanceCounts;
  records: { id: number; date: string; status: AttendanceStatus; marked_by: string | null }[];
}

export type ProgressStatus = 'not_started' | 'in_progress' | 'done';

export interface ChapterProgressItem {
  chapter_id: number;
  number: number;
  title: string;
  status: ProgressStatus;
  planned_date: string | null;
  started_on: string | null;
  completed_on: string | null;
}

export interface SubjectProgress {
  section_id: number;
  section_name: string;
  subject_id: number;
  subject_name: string;
  teacher_id: number | null;
  teacher_name: string | null;
  chapter_count: number;
  done_count: number;
  percentage: number;
  chapters: ChapterProgressItem[];
}

export interface SectionProgressSubject {
  subject_id: number;
  subject_name: string;
  teacher_name: string | null;
  chapter_count: number;
  done_count: number;
  in_progress_count: number;
  percentage: number;
}

export interface DiaryEntry {
  id: number;
  section_id: number;
  section_name: string;
  subject_id: number;
  subject_name: string;
  teacher_id: number;
  teacher_name: string;
  date: string;
  classwork: string | null;
  homework: string | null;
}

export interface ClassTest {
  id: number;
  title: string;
  date: string;
  total_marks: string;
  section_id: number;
  section_name: string;
  subject_id: number;
  subject_name: string;
  teacher_id: number;
  teacher_name: string;
  chapter_id: number | null;
  chapter_title: string | null;
  marks_entered: number;
  average: number | null;
  my_marks?: string | null;      // only in a student's own list
  was_absent?: boolean;
}

export interface ClassTestDetails extends ClassTest {
  students: { student_id: number; name: string; roll_number: string | null; obtained_marks: string | null; is_absent: boolean }[];
}

export interface TimetableSlot {
  id: number;
  section_id: number;
  section_name: string;
  day: number;
  day_name: string;
  period: number;
  subject_id: number;
  subject_name: string;
  teacher_id: number | null;
  teacher_name: string | null;
}

export interface Timetable {
  section_id?: number;
  section_name?: string;
  days: { day: number; name: string }[];
  periods_per_day: number;
  slots: TimetableSlot[];
}
