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
  ArrowRight,
  Activity,
  Clock,
  CheckCircle2,
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
      title: 'Total Students',
      value: stats.students,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      path: userRole === 'admin' ? '/admin/students' : undefined,
    },
    {
      title: 'Total Teachers',
      value: stats.teachers,
      icon: GraduationCap,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      path: userRole === 'admin' ? '/admin/teachers' : undefined,
    },
    {
      title: 'Active Courses',
      value: stats.courses,
      icon: BookOpen,
      color: 'text-violet-600',
      bgColor: 'bg-violet-50',
      path: userRole === 'admin' ? '/admin/courses' : undefined,
    },
    {
      title: 'Assignments',
      value: stats.assignments,
      icon: FileText,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
      path: userRole === 'teacher' ? '/teacher/assignments' : userRole === 'student' ? '/student/assignments' : undefined,
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.name || user?.username || 'User'}!
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Here's what's happening with your LMS today.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1 bg-white border border-gray-200 rounded-full flex items-center gap-2 shadow-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs font-medium text-gray-600 capitalize">{userRole} Mode</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              onClick={card.path ? () => navigate(card.path!) : undefined}
              className={`bg-white p-5 rounded-xl border border-gray-100 shadow-sm transition-all duration-200 ${
                card.path ? 'cursor-pointer hover:shadow-md hover:border-primary-100' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className={`${card.bgColor} ${card.color} p-2.5 rounded-lg`}>
                  <Icon size={20} />
                </div>
                {card.path && <ArrowRight size={16} className="text-gray-300" />}
              </div>
              <div className="mt-4">
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                <p className="text-sm font-medium text-gray-500 mt-0.5">{card.title}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Actions */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {userRole === 'admin' && (
                <>
                  <button onClick={() => navigate('/admin/students')} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Users size={18} /></div>
                      <span className="font-medium text-gray-700">Manage Students</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-300 group-hover:text-primary-500 transition-colors" />
                  </button>
                  <button onClick={() => navigate('/admin/teachers')} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><GraduationCap size={18} /></div>
                      <span className="font-medium text-gray-700">Manage Teachers</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-300 group-hover:text-primary-500 transition-colors" />
                  </button>
                </>
              )}
              {userRole === 'teacher' && (
                <>
                  <button onClick={() => navigate('/teacher/assignments')} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-amber-50 text-amber-600 rounded-lg"><FileText size={18} /></div>
                      <span className="font-medium text-gray-700">Create Assignment</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-300 group-hover:text-primary-500 transition-colors" />
                  </button>
                  <button onClick={() => navigate('/teacher/attendance')} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg"><Clock size={18} /></div>
                      <span className="font-medium text-gray-700">Mark Attendance</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-300 group-hover:text-primary-500 transition-colors" />
                  </button>
                </>
              )}
              {userRole === 'student' && (
                <>
                  <button onClick={() => navigate('/student/assignments')} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-amber-50 text-amber-600 rounded-lg"><FileText size={18} /></div>
                      <span className="font-medium text-gray-700">View Assignments</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-300 group-hover:text-primary-500 transition-colors" />
                  </button>
                  <button onClick={() => navigate('/student/results')} className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors group">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-rose-50 text-rose-600 rounded-lg"><Award size={18} /></div>
                      <span className="font-medium text-gray-700">View Results</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-300 group-hover:text-primary-500 transition-colors" />
                  </button>
                </>
              )}
            </div>
          </section>
        </div>

        {/* Sidebar Area */}
        <div className="space-y-8">
          {/* Announcements / Events */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Events</h2>
            <div className="space-y-3">
              {stats.events > 0 ? (
                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary-50 text-primary-600 rounded-lg">
                      <Calendar size={18} />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{stats.events} Scheduled Events</p>
                      <button onClick={() => navigate(userRole === 'admin' ? '/admin/events' : '#')} className="text-xs text-primary-600 font-medium hover:underline">View Calendar</button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-50 border border-dashed border-gray-200 p-6 rounded-xl text-center">
                  <Calendar size={24} className="mx-auto text-gray-300 mb-2" />
                  <p className="text-sm text-gray-500">No upcoming events</p>
                </div>
              )}
            </div>
          </section>

          {/* System Status */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Server Status</span>
                <span className="flex items-center gap-1.5 text-xs font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                  ONLINE
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database</span>
                <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">CONNECTED</span>
              </div>
              <div className="pt-4 border-t border-gray-50">
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Last Sync</span>
                  <span>Just now</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
