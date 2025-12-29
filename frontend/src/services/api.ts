import axios from 'axios';
import type {
  LoginCredentials,
  AuthResponse,
  Student,
  Teacher,
  Section,
  Course,
  Subject,
  Enrollment,
  Assignment,
  Submission,
  Attendance,
  Result,
  Announcement,
  Event,
} from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for slower database queries
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
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
        throw new Error('Cannot connect to server. Please make sure the backend is running on http://localhost:5000');
      }
      throw error;
    }
    
    // Handle JWT signature verification failed (422) or unauthorized (401)
    if (error.response?.status === 401 || error.response?.status === 422) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
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

// Admin
export const addAdmin = async (data: { name: string; username: string; email: string; password: string }) => {
  const response = await api.post('/add/admin', data);
  return response.data;
};

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
  console.log('Fetching subjects from:', `${API_BASE_URL}${url}`, params);
  const response = await api.get(url, { params });
  console.log('Subjects API response:', response.data);
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
export const enrollStudent = async (data: { student_name: string; course_name: string; enrollment_date: string; status: string; grade: string }) => {
  const response = await api.post('/enroll/student', data);
  return response.data;
};

export const getEnrollments = async (course_name?: string, student_name?: string) => {
  const url = '/get/enrollments';
  const params: any = {};
  if (course_name) params.course_name = course_name;
  if (student_name) params.student_name = student_name;
  console.log('Fetching enrollments from:', `${API_BASE_URL}${url}`, params);
  const response = await api.get(url, { params });
  console.log('Enrollments API response:', response.data);
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
  console.log('Fetching assignments from:', `${API_BASE_URL}${url}`, params);
  const response = await api.get(url, { params });
  console.log('Assignments API response:', response.data);
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
    console.log('Calling getSubmissionsByStudent with id:', id);
    const response = await api.get('/get/submissions/by/student', { params: id ? { id } : {} });
    console.log('getSubmissionsByStudent response:', response);
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

export const deleteSubmission = async (id: number) => {
  const response = await api.delete('/delete/submission', { params: { id } });
  return response.data;
};

// Attendance
export const markAttendance = async (data: { student_name: string; subject_name: string; status: 'present' | 'absent' | 'late' }) => {
  const response = await api.post('/attendance', data);
  return response.data;
};

export const getAttendance = async (student_name?: string, subject_name?: string) => {
  const response = await api.get('/get/attendance', { params: { student_name, subject_name } });
  return response.data;
};

export const updateAttendance = async (id: number, data: { status?: 'present' | 'absent' | 'late'; student_name?: string; subject_name?: string }) => {
  const response = await api.put('/update/attendance', data, { params: { id } });
  return response.data;
};

export const deleteAttendance = async (id: number, student_name?: string, subject_name?: string) => {
  const response = await api.delete('/delete/attendance', { params: { id, student_name, subject_name } });
  return response.data;
};

// Result
export const createResult = async (data: { student_name: string; subject_name: string; total_marks: number; obtained_marks: number; exam_type: string; remarks: string }) => {
  console.log('Creating result with data:', data);
  console.log('API endpoint: POST', `${API_BASE_URL}/create/result`);
  try {
    const response = await api.post('/create/result', data);
    console.log('Create result API response:', response.data);
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
  console.log('Fetching results from:', `${API_BASE_URL}${url}`, params);
  const response = await api.get(url, { params });
  console.log('Results API response:', response.data);
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

export const updateAnnouncement = async (id: number, data: { title?: string; content?: string; section_name?: string }) => {
  const response = await api.put('/update/announcement', data, { params: { id } });
  return response.data;
};

export const deleteAnnouncement = async (id: number) => {
  const response = await api.delete('/delete/announcement', { params: { id } });
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
export const chatWithBot = async (message: string) => {
  const response = await api.post('/chat', { message }, {
    timeout: 120000, // 120 seconds (2 minutes) for chatbot responses
  });
  return response.data;
};

