import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { RoleRedirect } from './components/RoleRedirect';
import Homepage from './pages/Homepage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Admin pages
import AdminStudents from './pages/admin/Students';
import AdminTeachers from './pages/admin/Teachers';
import AdminSections from './pages/admin/Sections';
import AdminCourses from './pages/admin/Courses';
import AdminSubjects from './pages/admin/Subjects';
import AdminEnrollments from './pages/admin/Enrollments';
import AdminEvents from './pages/admin/Events';

// Teacher pages
import TeacherAssignments from './pages/teacher/Assignments';
import TeacherAttendance from './pages/teacher/Attendance';
import TeacherResults from './pages/teacher/Results';
import TeacherAnnouncements from './pages/teacher/Announcements';
import TeacherSubmissions from './pages/teacher/Submissions';

// Student pages
import StudentAssignments from './pages/student/Assignments';
import StudentResults from './pages/student/Results';
import StudentAttendance from './pages/student/Attendance';
import StudentAnnouncements from './pages/student/Announcements';

// Chatbot
import Chatbot from './pages/Chatbot';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        
        {/* Admin Routes */}
        <Route
          path="/admin/students"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminStudents />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/teachers"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminTeachers />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/sections"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminSections />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/courses"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminCourses />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/subjects"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminSubjects />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/enrollments"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminEnrollments />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/events"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminEvents />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Teacher Routes */}
        <Route
          path="/teacher/assignments"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherAssignments />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/attendance"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherAttendance />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/results"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/announcements"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherAnnouncements />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/submissions"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherSubmissions />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Student Routes */}
        <Route
          path="/student/assignments"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentAssignments />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/results"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentResults />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/attendance"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentAttendance />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/announcements"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentAnnouncements />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Chatbot */}
        <Route
          path="/chatbot"
          element={
            <ProtectedRoute>
              <Layout>
                <Chatbot />
              </Layout>
            </ProtectedRoute>
          }
        />

      </Routes>
    </AuthProvider>
  );
}

export default App;

