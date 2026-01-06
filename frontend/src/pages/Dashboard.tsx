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
      {/* Welcome Header with gradient background */}
      <div className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 rounded-3xl p-8 text-white overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full -ml-48 -mb-48 blur-3xl"></div>
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">
                  Welcome back, {user?.name || user?.username || 'User'}!
                </h1>
                <p className="text-primary-100 text-sm mt-1">
                  Here's your overview for today
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold capitalize">{userRole} Mode</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid with improved design */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          const gradients = [
            'from-blue-500 to-blue-600',
            'from-emerald-500 to-emerald-600',
            'from-violet-500 to-violet-600',
            'from-amber-500 to-amber-600'
          ];
          return (
            <div
              key={card.title}
              onClick={card.path ? () => navigate(card.path!) : undefined}
              className={`group relative bg-white rounded-2xl border-2 border-gray-100 shadow-sm overflow-hidden transition-all duration-300 ${
                card.path ? 'cursor-pointer hover:shadow-2xl hover:border-primary-200 hover:-translate-y-2' : ''
              }`}
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${gradients[idx]} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
              
              <div className="relative p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`${card.bgColor} ${card.color} p-3 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                    <Icon size={24} />
                  </div>
                  {card.path && (
                    <ArrowRight size={18} className="text-gray-300 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
                  )}
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">{card.value}</p>
                  <p className="text-sm font-semibold text-gray-500">{card.title}</p>
                </div>
                {/* Progress bar animation */}
                <div className="mt-4 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div className={`h-full bg-gradient-to-r ${gradients[idx]} rounded-full transition-all duration-1000 ease-out`} style={{ width: card.path ? '75%' : '50%' }}></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Actions with enhanced styling */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Activity className="w-6 h-6 text-primary-600" />
                Quick Actions
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {userRole === 'admin' && (
                <>
                  <button onClick={() => navigate('/admin/students')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 border-2 border-blue-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Users size={22} className="text-blue-600" />
                      </div>
                      <span className="font-bold text-gray-800">Manage Students</span>
                    </div>
                    <ArrowRight size={18} className="text-blue-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/admin/teachers')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-emerald-50 to-emerald-100/50 border-2 border-emerald-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <GraduationCap size={22} className="text-emerald-600" />
                      </div>
                      <span className="font-bold text-gray-800">Manage Teachers</span>
                    </div>
                    <ArrowRight size={18} className="text-emerald-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/admin/courses')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-violet-50 to-violet-100/50 border-2 border-violet-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <BookOpen size={22} className="text-violet-600" />
                      </div>
                      <span className="font-bold text-gray-800">Manage Courses</span>
                    </div>
                    <ArrowRight size={18} className="text-violet-400 group-hover:text-violet-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/admin/enrollments')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-amber-50 to-amber-100/50 border-2 border-amber-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <FileText size={22} className="text-amber-600" />
                      </div>
                      <span className="font-bold text-gray-800">Manage Enrollments</span>
                    </div>
                    <ArrowRight size={18} className="text-amber-400 group-hover:text-amber-600 group-hover:translate-x-1 transition-all" />
                  </button>
                </>
              )}
              {userRole === 'teacher' && (
                <>
                  <button onClick={() => navigate('/teacher/assignments')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-amber-50 to-amber-100/50 border-2 border-amber-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <FileText size={22} className="text-amber-600" />
                      </div>
                      <span className="font-bold text-gray-800">Create Assignment</span>
                    </div>
                    <ArrowRight size={18} className="text-amber-400 group-hover:text-amber-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/teacher/attendance')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-indigo-50 to-indigo-100/50 border-2 border-indigo-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Clock size={22} className="text-indigo-600" />
                      </div>
                      <span className="font-bold text-gray-800">Mark Attendance</span>
                    </div>
                    <ArrowRight size={18} className="text-indigo-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/teacher/results')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-rose-50 to-rose-100/50 border-2 border-rose-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Award size={22} className="text-rose-600" />
                      </div>
                      <span className="font-bold text-gray-800">Manage Results</span>
                    </div>
                    <ArrowRight size={18} className="text-rose-400 group-hover:text-rose-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/teacher/announcements')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 border-2 border-blue-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Bell size={22} className="text-blue-600" />
                      </div>
                      <span className="font-bold text-gray-800">Post Announcement</span>
                    </div>
                    <ArrowRight size={18} className="text-blue-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                  </button>
                </>
              )}
              {userRole === 'student' && (
                <>
                  <button onClick={() => navigate('/student/assignments')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-amber-50 to-amber-100/50 border-2 border-amber-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <FileText size={22} className="text-amber-600" />
                      </div>
                      <span className="font-bold text-gray-800">View Assignments</span>
                    </div>
                    <ArrowRight size={18} className="text-amber-400 group-hover:text-amber-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/student/results')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-rose-50 to-rose-100/50 border-2 border-rose-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Award size={22} className="text-rose-600" />
                      </div>
                      <span className="font-bold text-gray-800">View Results</span>
                    </div>
                    <ArrowRight size={18} className="text-rose-400 group-hover:text-rose-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/student/attendance')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-indigo-50 to-indigo-100/50 border-2 border-indigo-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Clock size={22} className="text-indigo-600" />
                      </div>
                      <span className="font-bold text-gray-800">View Attendance</span>
                    </div>
                    <ArrowRight size={18} className="text-indigo-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" />
                  </button>
                  <button onClick={() => navigate('/student/announcements')} className="group flex items-center justify-between p-5 bg-gradient-to-br from-blue-50 to-blue-100/50 border-2 border-blue-200 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white rounded-xl shadow-md group-hover:scale-110 transition-transform">
                        <Bell size={22} className="text-blue-600" />
                      </div>
                      <span className="font-bold text-gray-800">View Announcements</span>
                    </div>
                    <ArrowRight size={18} className="text-blue-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                  </button>
                </>
              )}
            </div>
          </section>
        </div>

        {/* Sidebar Area */}
        <div className="space-y-8">
          {/* Announcements / Events with improved design */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Calendar className="w-6 h-6 text-primary-600" />
              Upcoming Events
            </h2>
            <div className="space-y-4">
              {stats.events > 0 ? (
                <div className="bg-gradient-to-br from-primary-50 to-primary-100/50 p-6 rounded-2xl border-2 border-primary-200 shadow-lg hover:shadow-xl transition-all">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-white rounded-xl shadow-md">
                      <Calendar size={24} className="text-primary-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-lg font-bold text-gray-900">{stats.events} Scheduled Events</p>
                      <p className="text-sm text-gray-600 mt-1">Stay updated with upcoming activities</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => navigate(userRole === 'admin' ? '/admin/events' : '#')} 
                    className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 transition-colors shadow-md"
                  >
                    View Calendar
                    <ArrowRight size={18} />
                  </button>
                </div>
              ) : (
                <div className="bg-white border-2 border-dashed border-gray-200 p-8 rounded-2xl text-center hover:border-gray-300 transition-colors">
                  <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Calendar size={32} className="text-gray-300" />
                  </div>
                  <p className="text-sm font-semibold text-gray-900 mb-1">No Upcoming Events</p>
                  <p className="text-xs text-gray-500">Events will appear here when scheduled</p>
                </div>
              )}
              
              {stats.announcements > 0 && (
                <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 p-6 rounded-2xl border-2 border-blue-200 shadow-lg hover:shadow-xl transition-all">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-white rounded-xl shadow-md">
                      <Bell size={24} className="text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-lg font-bold text-gray-900">{stats.announcements} New Announcements</p>
                      <p className="text-sm text-gray-600 mt-1">Check the latest updates</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => navigate(`/${userRole}/announcements`)} 
                    className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-colors shadow-md"
                  >
                    View All
                    <ArrowRight size={18} />
                  </button>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
