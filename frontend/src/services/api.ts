import axios from 'axios';
import type {
  LoginCredentials,
  AuthResponse,
} from '../types';
import { getSavedLogin, clearSavedLogin } from '../utils/session';

// The backend's address. Set VITE_API_URL in frontend/.env for a real server,
// for example VITE_API_URL=https://lms.example.com/api
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for slower database queries
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = getSavedLogin();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration and network errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle timeout errors
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.error('Request timeout:', error);
      const timeoutError = new Error('Request timed out. The server is taking too long to respond. Please try again.');
      (timeoutError as any).isTimeout = true;
      return Promise.reject(timeoutError);
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error);
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        throw new Error('Cannot connect to the server. Please make sure the backend is running.');
      }
      throw error;
    }
    
    // The login is no longer valid: 401 (expired or missing token), or 422 with a
    // "msg" field (Flask-JWT's answer for a broken token). Other 422 errors are
    // ordinary form validation errors and must not log the user out.
    const status = error.response?.status;
    const isBadToken = status === 422 && error.response?.data && typeof error.response.data.msg === 'string';

    if (status === 401 || isBadToken) {
      clearSavedLogin();

      // Only redirect if not already on login page. "expired=1" tells the login page to explain why.
      if (window.location.pathname !== '/login') {
        window.location.href = '/login?expired=1';
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/login', credentials);
  return response.data;
};

// Log out on the server too, so the token stops working straight away.
// A token can be passed in when it is no longer saved (for example after the user left the site).
export const logoutOnServer = async (token?: string) => {
  const headers: any = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  await api.post('/logout', {}, { headers });
};

// Tell the server this tab is being closed or left. Its login is then blocked
// a few seconds later, unless the page comes back (a refresh) and calls
// keepLoginAfterRefresh. sendBeacon still gets through while the page closes;
// it can't send headers, so the token goes in the body.
export const sendTabClosingSignal = (token: string) => {
  if (navigator.sendBeacon) {
    navigator.sendBeacon(API_BASE_URL + '/logout/closing', new Blob([token], { type: 'text/plain' }));
  }
};

// The page was refreshed: cancel the block that the closing signal scheduled
export const keepLoginAfterRefresh = async () => {
  await api.post('/logout/stay');
};

// My Account (any logged-in user)
export const getMyAccount = async () => {
  const response = await api.get('/account');
  return response.data;
};

export const updateMyUsername = async (username: string) => {
  const response = await api.put('/account/username', { username });
  return response.data;
};

export const changeMyPassword = async (current_password: string, new_password: string) => {
  const response = await api.put('/account/password', { current_password, new_password });
  return response.data;
};

// Admin
// The admin account is created once with "python create_admin.py", not from the app.
export const getAdmins = async (id?: number) => {
  const response = await api.get('/get/admin', { params: id ? { id } : {} });
  return response.data;
};

// Student
export const addStudent = async (data: { name: string; username: string; email: string; password: string; section_name: string }) => {
  const response = await api.post('/add/student', data);
  return response.data;
};

export const getStudents = async (id?: number) => {
  const response = await api.get('/get/student', { params: id ? { id } : {} });
  return response.data;
};

export const updateStudent = async (id: number, data: { name?: string; email?: string; section_name?: string; password?: string }) => {
  const response = await api.put('/update/student', data, { params: { id } });
  return response.data;
};

export const deleteStudent = async (id: number) => {
  const response = await api.delete('/delete/student', { params: { id } });
  return response.data;
};

// Teacher
export const addTeacher = async (data: { name: string; username: string; email: string; password: string }) => {
  const response = await api.post('/add/teacher', data);
  return response.data;
};

export const getTeachers = async (id?: number) => {
  const response = await api.get('/get/teacher', { params: id ? { id } : {} });
  return response.data;
};

export const updateTeacher = async (id: number, data: { name?: string; email?: string; password?: string }) => {
  const response = await api.put('/update/teacher', data, { params: { id } });
  return response.data;
};

export const deleteTeacher = async (id: number) => {
  const response = await api.delete('/delete/teacher', { params: { id } });
  return response.data;
};

// Section
export const addSection = async (data: { name: string; teacher_name: string }) => {
  const response = await api.post('/add/section', data);
  return response.data;
};

export const getSections = async (id?: number) => {
  const response = await api.get('/get/section', { params: id ? { id } : {} });
  return response.data;
};

export const updateSection = async (id: number, data: { name?: string; teacher_name?: string }) => {
  const response = await api.put('/update/section', data, { params: { id } });
  return response.data;
};

export const deleteSection = async (id: number) => {
  const response = await api.delete('/delete/section', { params: { id } });
  return response.data;
};

// Course
export const addCourse = async (data: { name: string; description: string; course_code: string; teacher_name: string; created_at: string }) => {
  const response = await api.post('/add/course', data);
  return response.data;
};

export const getCourses = async (id?: number) => {
  const response = await api.get('/get/courses', { params: id ? { id } : {} });
  return response.data;
};

export const updateCourse = async (id: number, data: { name?: string; description?: string; teacher_name?: string }) => {
  const response = await api.put('/update/course', data, { params: { id } });
  return response.data;
};

export const deleteCourse = async (id: number) => {
  const response = await api.delete('/delete/course', { params: { id } });
  return response.data;
};

// Subject
export const createSubject = async (data: { name: string; teacher_name: string; course_name: string }) => {
  const response = await api.post('/create/subject', data);
  return response.data;
};

export const getSubjects = async (id?: number) => {
  const url = '/get/subjects';
  const params = id ? { id } : {};
  const response = await api.get(url, { params });
  return response.data;
};

export const updateSubject = async (id: number, data: { name?: string; teacher_name?: string; course_name?: string }) => {
  const response = await api.put('/update/subject', data, { params: { id } });
  return response.data;
};

export const deleteSubject = async (id: number) => {
  const response = await api.delete('/delete/subject', { params: { id } });
  return response.data;
};

// Enrollment
export const enrollStudent = async (data: { student_id?: number; student_name?: string; course_name: string; enrollment_date: string; status: string; grade: string }) => {
  const response = await api.post('/enroll/student', data);
  return response.data;
};

export const getEnrollments = async (course_name?: string, student_name?: string) => {
  const url = '/get/enrollments';
  const params: any = {};
  if (course_name) params.course_name = course_name;
  if (student_name) params.student_name = student_name;
  const response = await api.get(url, { params });
  return response.data;
};

export const updateEnrollment = async (id: number, data: { status?: string; grade?: string }) => {
  const response = await api.put('/update/enrollment', data, { params: { id } });
  return response.data;
};

export const deleteEnrollment = async (id: number) => {
  const response = await api.delete('/delete/enrollment', { params: { id } });
  return response.data;
};

// Assignment
export const createAssignment = async (data: { title: string; description: string; due_date: string; subject_name: string; total_marks: number }) => {
  const response = await api.post('/create/assignments', data);
  return response.data;
};

export const getAssignments = async (id?: number) => {
  const url = '/get/assignments';
  const params = id ? { id } : {};
  const response = await api.get(url, { params });
  return response.data;
};

export const updateAssignment = async (id: number, data: { title?: string; description?: string; due_date?: string; subject_name?: string; total_marks?: number }) => {
  const response = await api.put('/update/assignments/', data, { params: { id } });
  return response.data;
};

export const deleteAssignment = async (id: number) => {
  const response = await api.delete('/delete/assignments/', { params: { id } });
  return response.data;
};

// Submission
export const submitAssignment = async (formData: FormData) => {
  const response = await api.post('/submit/assignment', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getSubmissionsByStudent = async (id?: number) => {
  try {
    const response = await api.get('/get/submissions/by/student', { params: id ? { id } : {} });
    return response.data;
  } catch (error: any) {
    console.error('getSubmissionsByStudent error:', error);
    console.error('Error config:', error.config);
    console.error('Error response:', error.response);
    throw error;
  }
};

export const getSubmissionsByAssignment = async (id: number) => {
  const response = await api.get('/get/submissions/by/assignment', { params: { id } });
  return response.data;
};

export const updateSubmission = async (id: number, data: { submission_text?: string; marks_obtained?: number; feedback?: string }) => {
  const response = await api.put('/update/submission', data, { params: { id } });
  return response.data;
};

// Download a submission's file. Files are private, so this goes through the
// logged-in API (with the token) and then saves the file in the browser.
export const downloadSubmissionFile = async (id: number) => {
  const response = await api.get('/submission/file', { params: { id }, responseType: 'blob' });

  // Read the original file name from the server's "Content-Disposition" header
  let fileName = 'submission';
  const disposition = response.headers['content-disposition'];
  if (disposition) {
    const match = disposition.match(/filename="?([^";]+)"?/);
    if (match) {
      fileName = match[1];
    }
  }

  const fileUrl = window.URL.createObjectURL(response.data);
  const link = document.createElement('a');
  link.href = fileUrl;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(fileUrl);
};

export const deleteSubmission = async (id: number) => {
  const response = await api.delete('/delete/submission', { params: { id } });
  return response.data;
};

// Attendance
export const markAttendance = async (data: { student_id?: number; student_name?: string; subject_name: string; status: 'present' | 'absent' | 'late' }) => {
  const response = await api.post('/attendance', data);
  return response.data;
};

export const getAttendance = async (student_name?: string, subject_name?: string) => {
  const response = await api.get('/get/attendance', { params: { student_name, subject_name } });
  return response.data;
};

export const updateAttendance = async (id: number, data: { status?: 'present' | 'absent' | 'late'; student_id?: number; student_name?: string; subject_name?: string }) => {
  const response = await api.put('/update/attendance', data, { params: { id } });
  return response.data;
};

export const deleteAttendance = async (id: number, student_name?: string, subject_name?: string) => {
  const response = await api.delete('/delete/attendance', { params: { id, student_name, subject_name } });
  return response.data;
};

// Result
export const createResult = async (data: { student_id?: number; student_name?: string; subject_name: string; total_marks: number; obtained_marks: number; exam_type: string; remarks: string }) => {
  try {
    const response = await api.post('/create/result', data);
    return response.data;
  } catch (error: any) {
    console.error('Create result API error:', error);
    console.error('Error response:', error.response);
    throw error;
  }
};

export const getResults = async (id?: number) => {
  const url = '/get/result';
  const params = id ? { id } : {};
  const response = await api.get(url, { params });
  return response.data;
};

export const updateResult = async (id: number, data: { obtained_marks?: number; remarks?: string }) => {
  const response = await api.put('/update/result', data, { params: { id } });
  return response.data;
};

export const deleteResult = async (id: number) => {
  const response = await api.delete('/delete/result', { params: { id } });
  return response.data;
};

// Announcement
export const createAnnouncement = async (data: { title: string; content: string; target_audience: string; section_name: string }) => {
  const response = await api.post('/create/announcement', data);
  return response.data;
};

export const getAnnouncements = async (id?: number) => {
  const response = await api.get('/get/announcements', { params: id ? { id } : {} });
  return response.data;
};

// The backend finds announcements by their title, not by id
export const updateAnnouncement = async (title: string, data: { title?: string; content?: string; section_name?: string }) => {
  const response = await api.put('/update/announcement', data, { params: { title } });
  return response.data;
};

export const deleteAnnouncement = async (title: string) => {
  const response = await api.delete('/delete/announcement', { params: { title } });
  return response.data;
};

// Event
export const createEvent = async (data: { title: string; description: string; event_date: string; event_time: string }) => {
  const response = await api.post('/create/event', data);
  return response.data;
};

export const getEvents = async (id?: number) => {
  const response = await api.get('/get/events', { params: id ? { id } : {} });
  return response.data;
};

export const updateEvent = async (id: number, data: { title?: string; description?: string; event_date?: string; event_time?: string }) => {
  const response = await api.put('/update/event', data, { params: { id } });
  return response.data;
};

export const deleteEvent = async (id: number) => {
  const response = await api.delete('/delete/event', { params: { id } });
  return response.data;
};

// Chatbot - Extended timeout for AI processing
// The conversation is saved on the server, so only the new message is sent
export const chatWithBot = async (message: string) => {
  const response = await api.post('/chat', { message }, {
    timeout: 120000, // 120 seconds (2 minutes) for chatbot responses
  });
  return response.data;
};

export const getChatHistory = async () => {
  const response = await api.get('/chat/history');
  return response.data;
};

export const clearChatHistory = async () => {
  const response = await api.delete('/chat/history');
  return response.data;
};

// The user clicked Confirm (approve = true) or Cancel on a delete or edit the assistant asked for
export const answerChatAction = async (action_id: number, approve: boolean) => {
  const response = await api.post('/chat/confirm', { action_id, approve });
  return response.data;
};


// ---------------- School structure (Classes 1-10)

export const getSchoolClasses = async () => {
  const response = await api.get('/school/classes');
  return response.data;
};

export const getSchoolClass = async (classId: number) => {
  const response = await api.get(`/school/classes/${classId}`);
  return response.data;
};

export const addClassSection = async (classId: number, data: { name: string; incharge_id?: number | null }) => {
  const response = await api.post(`/school/classes/${classId}/sections`, data);
  return response.data;
};

export const getClassSection = async (sectionId: number) => {
  const response = await api.get(`/school/sections/${sectionId}`);
  return response.data;
};

export const updateClassSection = async (sectionId: number, data: { name?: string; incharge_id?: number | null }) => {
  const response = await api.put(`/school/sections/${sectionId}`, data);
  return response.data;
};

export const deleteClassSection = async (sectionId: number) => {
  const response = await api.delete(`/school/sections/${sectionId}`);
  return response.data;
};

// Choose who teaches a subject in a section (teacherId null removes the teacher)
export const setSubjectTeacher = async (sectionId: number, subjectId: number, teacherId: number | null) => {
  const response = await api.put(`/school/sections/${sectionId}/teachers`, { subject_id: subjectId, teacher_id: teacherId });
  return response.data;
};

export const addClassSubject = async (classId: number, name: string) => {
  const response = await api.post(`/school/classes/${classId}/subjects`, { name });
  return response.data;
};

export const renameClassSubject = async (subjectId: number, name: string) => {
  const response = await api.put(`/school/subjects/${subjectId}`, { name });
  return response.data;
};

export const deleteClassSubject = async (subjectId: number) => {
  const response = await api.delete(`/school/subjects/${subjectId}`);
  return response.data;
};

export const getSubjectChapters = async (subjectId: number) => {
  const response = await api.get(`/school/subjects/${subjectId}/chapters`);
  return response.data;
};

export const addSubjectChapter = async (subjectId: number, data: { title: string; description?: string }) => {
  const response = await api.post(`/school/subjects/${subjectId}/chapters`, data);
  return response.data;
};

export const updateSubjectChapter = async (chapterId: number, data: { title?: string; number?: number; description?: string }) => {
  const response = await api.put(`/school/chapters/${chapterId}`, data);
  return response.data;
};

export const deleteSubjectChapter = async (chapterId: number) => {
  const response = await api.delete(`/school/chapters/${chapterId}`);
  return response.data;
};

export const getAcademicSessions = async () => {
  const response = await api.get('/school/sessions');
  return response.data;
};

export const addAcademicSession = async (data: { name: string; start_date: string; end_date: string; is_current?: boolean }) => {
  const response = await api.post('/school/sessions', data);
  return response.data;
};

export const makeSessionCurrent = async (sessionId: number) => {
  const response = await api.put(`/school/sessions/${sessionId}/current`);
  return response.data;
};

// A teacher's own sections and subjects
export const getMyClasses = async () => {
  const response = await api.get('/school/my-classes');
  return response.data;
};

// A student's own class
export const getMyClass = async () => {
  const response = await api.get('/school/my-class');
  return response.data;
};
