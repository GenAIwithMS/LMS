import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ChatbotWidget from './ChatbotWidget';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpen,
  FileText,
  Calendar,
  Bell,
  MessageSquare,
  LogOut,
  Menu,
  X,
  UserCircle,
  Settings,
  ClipboardList,
  Award,
  Clock,
  ChevronRight,
  ChevronLeft,
  Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { logout, userRole, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const saved = localStorage.getItem('sidebarOpen');
    return saved !== null ? saved === 'true' : true;
  });
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved !== null ? saved === 'true' : false;
  });
  const [chatbotOpen, setChatbotOpen] = useState(() => {
    const saved = localStorage.getItem('chatbotOpen');
    return saved !== null ? saved === 'true' : false;
  });
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    localStorage.setItem('sidebarOpen', sidebarOpen.toString());
  }, [sidebarOpen]);

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.toString());
  }, [sidebarCollapsed]);

  useEffect(() => {
    localStorage.setItem('chatbotOpen', chatbotOpen.toString());
  }, [chatbotOpen]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  const adminMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/admin/students', label: 'Students', icon: Users },
    { path: '/admin/teachers', label: 'Teachers', icon: GraduationCap },
    { path: '/admin/sections', label: 'Sections', icon: BookOpen },
    { path: '/admin/courses', label: 'Courses', icon: BookOpen },
    { path: '/admin/subjects', label: 'Subjects', icon: FileText },
    { path: '/admin/enrollments', label: 'Enrollments', icon: ClipboardList },
    { path: '/admin/events', label: 'Events', icon: Calendar },
  ];

  const teacherMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/teacher/assignments', label: 'Assignments', icon: FileText },
    { path: '/teacher/attendance', label: 'Attendance', icon: Clock },
    { path: '/teacher/results', label: 'Results', icon: Award },
    { path: '/teacher/announcements', label: 'Announcements', icon: Bell },
    { path: '/teacher/submissions', label: 'Submissions', icon: ClipboardList },
  ];

  const studentMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/student/assignments', label: 'Assignments', icon: FileText },
    { path: '/student/results', label: 'Results', icon: Award },
    { path: '/student/attendance', label: 'Attendance', icon: Clock },
    { path: '/student/announcements', label: 'Announcements', icon: Bell },
  ];

  const menuItems = userRole === 'admin' ? adminMenuItems : userRole === 'teacher' ? teacherMenuItems : studentMenuItems;

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(true);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const sidebarWidth = sidebarCollapsed ? 'w-20' : 'w-64';

  return (
    <div className="min-h-screen bg-gray-50 flex overflow-hidden">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Navigation Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 ${sidebarWidth} bg-white border-r border-gray-200 transition-all duration-300 ease-in-out flex flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo Section */}
        <div className="h-16 flex items-center px-6 border-b border-gray-100 relative">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold">L</div>
            {!sidebarCollapsed && <span className="text-xl font-bold text-gray-900 tracking-tight">LMS Pro</span>}
          </div>
          
          {/* Sidebar Toggle Arrow - Inside Sidebar */}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="hidden lg:flex absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-white border border-gray-200 rounded-full items-center justify-center text-gray-400 hover:text-primary-600 hover:border-primary-200 shadow-sm z-50 transition-all"
          >
            {sidebarCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>

          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden ml-auto text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                  active
                    ? 'bg-primary-50 text-primary-700 font-semibold'
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                }`}
                title={sidebarCollapsed ? item.label : ''}
              >
                <Icon size={20} className={active ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'} />
                {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User Profile Section */}
        <div className="p-4 border-t border-gray-100">
          <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'justify-center' : 'px-2 py-2'}`}>
            <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 border border-gray-200">
              <UserCircle size={24} />
            </div>
            {!sidebarCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500 capitalize">{userRole}</p>
              </div>
            )}
          </div>
          <button
            onClick={handleLogout}
            className={`mt-2 w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-500 hover:bg-red-50 transition-colors ${sidebarCollapsed ? 'justify-center' : ''}`}
            title={sidebarCollapsed ? 'Logout' : ''}
          >
            <LogOut size={18} />
            {!sidebarCollapsed && <span className="text-sm font-medium">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-8 shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
            >
              <Menu size={20} />
            </button>
            <div className="hidden lg:block">
              <h2 className="text-sm font-medium text-gray-500">
                {location.pathname.split('/').filter(Boolean).map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' / ') || 'Dashboard'}
              </h2>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Notification Icon */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className={`p-2 rounded-full transition-colors relative ${showNotifications ? 'bg-gray-100 text-primary-600' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'}`}
              >
                <Bell size={20} />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
              </button>
              
              {/* Notification Dropdown */}
              {showNotifications && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)}></div>
                  <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in zoom-in duration-200">
                    <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                      <h3 className="font-bold text-gray-900">Notifications</h3>
                      <button className="text-xs text-primary-600 font-medium hover:underline">Mark all as read</button>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      <div className="p-4 text-center text-gray-500 text-sm">
                        <Bell size={32} className="mx-auto text-gray-200 mb-2" />
                        <p>No new notifications</p>
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 border-t border-gray-100 text-center">
                      <button className="text-xs font-bold text-gray-500 hover:text-gray-700 uppercase tracking-wider">View All Activity</button>
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="h-8 w-px bg-gray-200 mx-1"></div>
            
            {/* AI Assistant Icon - Replacing Settings */}
            <button 
              onClick={() => setChatbotOpen(!chatbotOpen)}
              className={`p-2 rounded-full transition-all ${chatbotOpen ? 'bg-indigo-50 text-indigo-600 ring-2 ring-indigo-100' : 'text-gray-400 hover:text-indigo-600 hover:bg-indigo-50'}`}
              title="AI Assistant"
            >
              <Sparkles size={20} />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8">
          {children}
        </div>

        {/* Chatbot Widget Integration */}
        <ChatbotWidget 
          isOpen={chatbotOpen} 
          onClose={() => setChatbotOpen(false)} 
        />
      </main>
    </div>
  );
};
