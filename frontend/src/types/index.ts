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
  section_id?: number | null;
  title: string;
  content: string;
  target_audience: string;      // "all", "teachers" or "students"
  section: string;
  teacher: string;
  created_at: string;
  // Who wrote it and where it goes (sent by the API)
  audience_text?: string;       // "Everyone", "Teachers", "Students"
  section_name?: string | null;
  class_id?: number | null;
  class_name?: string | null;
  where?: string;               // "Whole school", "Class 5 (all sections)" or "Class 5 - A"
  teacher_id?: number | null;
  teacher_name?: string | null;
  admin_id?: number | null;
  author_role?: 'admin' | 'teacher';
  author_name?: string | null;
  from_incharge?: boolean;      // a class announcement from the section's class incharge
  author_text?: string;         // "Principal (Admin)", "Sara Ahmed (Class incharge of Class 5 - A)"
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
  subject_teachers: { section_id: number; subject_id: number; teacher_id: number; teacher_name: string }[];
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

// One slot of the school day: a class period (numbered) or a break (no number)
export interface BellPeriod {
  number: number | null;
  name: string;
  start_time: string;          // "08:00"
  end_time: string;
  is_break: boolean;
}

export interface Timetable {
  section_id?: number;
  section_name?: string | null;
  days: { day: number; name: string }[];
  periods: BellPeriod[];
  periods_per_day: number;
  slots: TimetableSlot[];
  is_published?: boolean;      // for teachers and students: has the admin published one yet?
  published_at?: string | null;
}

export interface TimetableSettings {
  days: { day: number; name: string }[];
  periods: BellPeriod[];
  periods_per_day: number;
}

// A subject that can go in a section's period, with its teacher there
export interface PeriodSubject {
  subject_id: number;
  subject_name: string;
  teacher_id: number | null;
  teacher_name: string | null;
}

export interface PublishStatus {
  is_published: boolean;
  published_at: string | null;
  published_by: string | null;
  has_unpublished_changes: boolean;
}

export interface DraftSection {
  section_id: number;
  section_name: string;
  class_id: number;
  class_name: string;
  incharge_name: string | null;
  student_count: number;
  subjects: PeriodSubject[];
  slots: TimetableSlot[];
}

// A teacher with the subjects they teach (by name, like "Urdu")
export interface TeacherSkills {
  teacher_id: number;
  teacher_name: string;
  username?: string;
  subjects: string[];
}

export interface TeacherSubjectList {
  subject_names: string[];
  teachers: TeacherSkills[];
}

export interface SchoolTimetableDraft extends TimetableSettings {
  sections: DraftSection[];
  teachers: TeacherSkills[];
  teacher_load: { teacher_id: number; teacher_name: string; periods: number }[];
  status: PublishStatus;
}

// ---------------- Exams

export interface ExamTerm {
  id: number;
  session_id: number;
  session_name: string;
  name: string;
  start_date: string;
  end_date: string;
  marks_deadline: string | null;
  is_locked: boolean;
  is_closed: boolean;          // locked, or the marks deadline has passed
  is_published: boolean;
  paper_count: number;
}

export type QuestionStatus = 'none' | 'submitted' | 'approved' | 'returned';

export interface ExamPaper {
  id: number;
  term_id: number;
  term_name: string;
  class_id: number;
  class_name: string;
  subject_id: number;
  subject_name: string;
  total_marks: string;
  passing_marks: string;
  exam_date: string | null;
  has_question_file: boolean;
  question_status: QuestionStatus;
  review_note: string | null;
  uploaded_by: string | null;
  marks_entered: number;
}

// A paper as a teacher sees it: one row per section they mark
export interface TeacherPaper extends ExamPaper {
  section_id: number;
  section_name: string;
  student_count: number;
}

export interface PaperMarksSheet extends ExamPaper {
  section_id: number;
  section_name: string;
  is_closed: boolean;
  students: { student_id: number; name: string; roll_number: string | null; obtained_marks: string | null; is_absent: boolean }[];
}

export interface SubjectResult {
  paper_id: number;
  subject_id: number;
  subject_name: string;
  total_marks: string;
  passing_marks: string;
  obtained_marks: string | null;
  is_absent: boolean;
  percentage: number | null;
  grade: string | null;
  passed: boolean | null;      // null: marks not entered yet
}

export type TermResultStatus = 'Pass' | 'Fail' | 'Incomplete';

export interface StudentTermResult {
  student_id: number;
  name: string;
  roll_number: string | null;
  subjects: SubjectResult[];
  total_marks: string;
  total_obtained: string;
  percentage: number | null;
  grade: string | null;
  result: TermResultStatus;
  position: number | null;
  remarks?: string | null;   // the class incharge's report card remarks
}

export interface SectionResultSheet {
  term: ExamTerm;
  section_id: number;
  section_name: string;
  incharge_name: string | null;
  subjects: { paper_id: number; subject_name: string; total_marks: string }[];
  students: StudentTermResult[];
  passed_count: number;
}

export interface GradeBand {
  grade: string;
  min_percentage: number;
}

export interface ReportCard extends StudentTermResult {
  term: ExamTerm;
  section_id: number;
  section_name: string;
  class_strength: number;
  incharge_name: string | null;
  admission_number: string | null;
  guardian_name: string | null;
  attendance: AttendanceCounts;
  remarks: string | null;
  grade_scale: GradeBand[];    // the school's scale, highest grade first
}

export interface TermAnalysis {
  term: ExamTerm;
  sections: {
    section_id: number;
    section_name: string;
    student_count: number;
    passed_count: number;
    subjects: {
      subject_name: string;
      teacher_name: string | null;
      marked_count: number;
      average_percentage: number | null;
      pass_percentage: number | null;
      highest_marks: string | null;
      total_marks: string;
    }[];
    top_students: { name: string; position: number; percentage: number | null }[];
  }[];
  teachers: {
    teacher_name: string;
    subjects: { section_name: string; subject_name: string; average_percentage: number | null; pass_percentage: number | null }[];
  }[];
}

export interface PromotionList {
  section_id: number;
  section_name: string;
  class_name: string;
  next_class_name: string | null;
  is_last_class: boolean;
  target_sections: ClassSection[];
  students: { student_id: number; name: string; roll_number: string | null; result: TermResultStatus | null; percentage: number | null; suggest_promote: boolean }[];
}

// ---------------- Oversight

export type ActivityAction = 'login' | 'login_failed' | 'logout' | 'create' | 'update' | 'delete';

export interface ActivityEntry {
  id: number;
  created_at: string;          // "2026-11-04 09:15"
  user_role: UserRole | null;
  user_id: number | null;
  user_name: string | null;    // for a failed login: the email that was tried
  action: ActivityAction;
  area: string;
  description: string;
  ip_address: string | null;
  section_id: number | null;
  class_id: number | null;
}

export interface ActivityPage {
  total: number;
  page: number;
  per_page: number;
  entries: ActivityEntry[];
}

export interface TeacherWeek {
  diary_entries: number;
  assignments: number;
  class_tests: number;
  progress_updates: number;
  attendance_days_marked: number;
  actions: number;
}

export interface TeacherOverview {
  id: number;
  name: string;
  username: string;
  email: string;
  last_login: string | null;
  last_active: string | null;
  incharge_of: string[];
  subjects_taught: number;
  this_week: TeacherWeek;
  attendance_not_marked_today: string[];
  papers_pending: number;
}

export interface TeachersOverview {
  week_start: string;
  today: string;
  teachers: TeacherOverview[];
}

export interface PendingMarks {
  term_name: string;
  subject_name: string;
  section_name: string;
  entered: number;
  student_count: number;
  teacher_name?: string | null;
}

export interface TeacherActivity extends TeacherOverview {
  teaching: { section_id: number; section_name: string; subject_name: string; chapters_done: number; chapter_count: number; percentage: number; periods_per_week: number }[];
  periods_per_week: number;
  marks_pending: PendingMarks[];
  diary_this_week: { date: string; section_name: string; subject_name: string; classwork: string | null; homework: string | null }[];
  assignments_this_week: { title: string; subject_name: string; section_name: string | null; due_date: string; created_at: string }[];
  recent_actions: ActivityEntry[];
}

export interface SectionAttendanceToday {
  section_id: number;
  section_name: string;
  incharge_name: string | null;
  student_count: number;
  marked_count: number;
  is_marked: boolean;
  present: number;
  absent: number;
  late: number;
  leave: number;
}

export interface ClassCoverage {
  class_id: number;
  class_name: string;
  average_percentage: number | null;
  sections: {
    section_id: number;
    section_name: string;
    average_percentage: number | null;
    subjects: { subject_name: string; teacher_name: string | null; chapters_done: number; chapter_count: number; percentage: number }[];
  }[];
}

export interface LowAttendanceStudent {
  student_id: number;
  name: string;
  roll_number: string | null;
  section_name: string | null;
  percentage: number;
  absent: number;
  days_counted: number;
}

export interface OversightDashboard {
  today: string;
  low_attendance_percent: number;
  counts: { students: number; teachers: number; sections: number; sections_marked_today: number; question_papers_waiting: number };
  attendance_today: SectionAttendanceToday[];
  syllabus_coverage: ClassCoverage[];
  marks_pending: PendingMarks[];
  low_attendance: LowAttendanceStudent[];
}
