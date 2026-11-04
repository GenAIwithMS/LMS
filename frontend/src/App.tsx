import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import Homepage from './pages/Homepage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Admin pages
import AdminStudents from './pages/admin/Students';
import AdminTeachers from './pages/admin/Teachers';
import AdminEvents from './pages/admin/Events';
import AdminClasses from './pages/admin/Classes';
import AdminClassDetail from './pages/admin/ClassDetail';
import SectionDetail from './pages/SectionDetail';
import TeacherMyClasses from './pages/teacher/MyClasses';
import AdminExams from './pages/admin/Exams';
import AdminExamTerm from './pages/admin/ExamTerm';
import AdminPromotion from './pages/admin/Promotion';
import ReportCardPage from './pages/ReportCardPage';
import StudentMyClass from './pages/student/MyClass';

// Teacher pages
import TeacherAssignments from './pages/teacher/Assignments';
import TeacherAttendance from './pages/teacher/Attendance';
import TeacherExams from './pages/teacher/Exams';
import TeacherAnnouncements from './pages/teacher/Announcements';
import TeacherSubmissions from './pages/teacher/Submissions';
import TeacherClassTests from './pages/teacher/ClassTests';

// Student pages
import StudentAssignments from './pages/student/Assignments';
import StudentReportCards from './pages/student/ReportCards';
import StudentAttendance from './pages/student/Attendance';
import StudentAnnouncements from './pages/student/Announcements';
import StudentClassTests from './pages/student/ClassTests';

// Chatbot
import Chatbot from './pages/Chatbot';
import Account from './pages/Account';

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
          path="/admin/classes"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminClasses />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/classes/:classId"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminClassDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/sections/:sectionId"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <SectionDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/classes"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherMyClasses />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/sections/:sectionId"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <SectionDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/class"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentMyClass />
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

        <Route
          path="/admin/exams"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminExams />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/exams/:termId"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminExamTerm />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/promotion"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Layout>
                <AdminPromotion />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* A report card, for the admin, the student's teachers and the student */}
        <Route
          path="/report-card/:termId/:studentId"
          element={
            <ProtectedRoute allowedRoles={['admin', 'teacher', 'student']}>
              <Layout>
                <ReportCardPage />
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
          path="/teacher/exams"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherExams />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/class-tests"
          element={
            <ProtectedRoute allowedRoles={['teacher']}>
              <Layout>
                <TeacherClassTests />
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
          path="/student/report-card"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentReportCards />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/class-tests"
          element={
            <ProtectedRoute allowedRoles={['student']}>
              <Layout>
                <StudentClassTests />
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

        {/* My Account (every role) */}
        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <Layout>
                <Account />
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

