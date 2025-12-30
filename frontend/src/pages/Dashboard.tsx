import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  GraduationCap,
  BookOpen,
  FileText,
  Calendar,
  Bell,
  TrendingUp,
  Award,
} from 'lucide-react';
import { getStudents, getTeachers, getCourses, getAssignments, getAnnouncements, getEvents } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const { userRole, user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    students: 0,
    teachers: 0,
    courses: 0,
    assignments: 0,
    announcements: 0,
    events: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [studentsRes, teachersRes, coursesRes, assignmentsRes, announcementsRes, eventsRes] = await Promise.allSettled([
          getStudents(),
          getTeachers(),
          getCourses(),
          getAssignments(),
          getAnnouncements(),
          getEvents(),
        ]);

        setStats({
          students: studentsRes.status === 'fulfilled' ? (Array.isArray(studentsRes.value) ? studentsRes.value.length : 1) : 0,
          teachers: teachersRes.status === 'fulfilled' ? (Array.isArray(teachersRes.value) ? teachersRes.value.length : 1) : 0,
          courses: coursesRes.status === 'fulfilled' ? (Array.isArray(coursesRes.value) ? coursesRes.value.length : 1) : 0,
          assignments: assignmentsRes.status === 'fulfilled' ? (Array.isArray(assignmentsRes.value) ? assignmentsRes.value.length : 1) : 0,
          announcements: announcementsRes.status === 'fulfilled' ? (Array.isArray(announcementsRes.value) ? announcementsRes.value.length : 1) : 0,
          events: eventsRes.status === 'fulfilled' ? (Array.isArray(eventsRes.value) ? eventsRes.value.length : 1) : 0,
        });
      } catch (error) {
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      title: 'Students',
      value: stats.students,
      icon: Users,
      color: 'bg-blue-500',
      path: userRole === 'admin' ? '/admin/students' : undefined,
    },
    {
      title: 'Teachers',
      value: stats.teachers,
      icon: GraduationCap,
      color: 'bg-green-500',
      path: userRole === 'admin' ? '/admin/teachers' : undefined,
    },
    {
      title: 'Courses',
      value: stats.courses,
      icon: BookOpen,
      color: 'bg-purple-500',
      path: userRole === 'admin' ? '/admin/courses' : undefined,
    },
    {
      title: 'Assignments',
      value: stats.assignments,
      icon: FileText,
      color: 'bg-orange-500',
      path: userRole === 'teacher' ? '/teacher/assignments' : userRole === 'student' ? '/student/assignments' : undefined,
    },
    {
      title: 'Announcements',
      value: stats.announcements,
      icon: Bell,
      color: 'bg-pink-500',
      path: userRole === 'teacher' ? '/teacher/announcements' : userRole === 'student' ? '/student/announcements' : undefined,
    },
    {
      title: 'Events',
      value: stats.events,
      icon: Calendar,
      color: 'bg-indigo-500',
      path: userRole === 'admin' ? '/admin/events' : undefined,
    },
  ].filter(card => card.path || userRole === 'admin');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name || user?.username || 'User'}!
        </h1>
        <p className="text-gray-600 mt-2">Here's an overview of your system.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((card) => {
          const Icon = card.icon;
          const CardComponent = card.path ? 'button' : 'div';
          const props = card.path
            ? {
                onClick: () => navigate(card.path!),
                className: 'cursor-pointer hover:scale-105 transition-transform',
              }
            : {};

          return (
            <CardComponent key={card.title} {...props}>
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{card.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                  </div>
                  <div className={`${card.color} p-4 rounded-lg`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                </div>
              </div>
            </CardComponent>
          );
        })}
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            {userRole === 'admin' && (
              <>
                <button
                  onClick={() => navigate('/admin/students')}
                  className="w-full btn btn-secondary text-left"
                >
                  Manage Students
                </button>
                <button
                  onClick={() => navigate('/admin/teachers')}
                  className="w-full btn btn-secondary text-left"
                >
                  Manage Teachers
                </button>
                <button
                  onClick={() => navigate('/admin/courses')}
                  className="w-full btn btn-secondary text-left"
                >
                  Manage Courses
                </button>
              </>
            )}
            {userRole === 'teacher' && (
              <>
                <button
                  onClick={() => navigate('/teacher/assignments')}
                  className="w-full btn btn-secondary text-left"
                >
                  Create Assignment
                </button>
                <button
                  onClick={() => navigate('/teacher/attendance')}
                  className="w-full btn btn-secondary text-left"
                >
                  Mark Attendance
                </button>
                <button
                  onClick={() => navigate('/teacher/announcements')}
                  className="w-full btn btn-secondary text-left"
                >
                  Create Announcement
                </button>
              </>
            )}
            {userRole === 'student' && (
              <>
                <button
                  onClick={() => navigate('/student/assignments')}
                  className="w-full btn btn-secondary text-left"
                >
                  View Assignments
                </button>
                <button
                  onClick={() => navigate('/student/results')}
                  className="w-full btn btn-secondary text-left"
                >
                  View Results
                </button>
                <button
                  onClick={() => navigate('/student/announcements')}
                  className="w-full btn btn-secondary text-left"
                >
                  View Announcements
                </button>
              </>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">System</span>
              <span className="text-sm font-semibold text-green-600">Operational</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Role</span>
              <span className="text-sm font-semibold text-blue-600 capitalize">{userRole}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

