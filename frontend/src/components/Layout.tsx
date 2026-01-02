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
  PanelLeft,
  Sparkles,
} from 'lucide-react';
import { getAnnouncements, getEvents } from '../services/api';
import toast from 'react-hot-toast';

// Manus Icon Component
const ManusIcon = ({ size = 20, className = "" }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
  </svg>
);

interface LayoutProps {
  children: React.ReactNode;
}

interface Notification {
  id: string | number;
  title: string;
  type: 'announcement' | 'event';
  time: string;
  creatorId?: number | string;
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
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [hasUnread, setHasUnread] = useState(false);

  useEffect(() => {
    localStorage.setItem('sidebarOpen', sidebarOpen.toString());
  }, [sidebarOpen]);

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.toString());
  }, [sidebarCollapsed]);

  useEffect(() => {
    localStorage.setItem('chatbotOpen', chatbotOpen.toString());
  }, [chatbotOpen]);

  // Fetch real-time notifications
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const [announcements, events] = await Promise.all([
          getAnnouncements(),
          getEvents()
        ]);
        
        const currentUserId = user?.id;

        const combined: Notification[] = [
          ...(Array.isArray(announcements) ? announcements
            .filter((a: any) => a.teacher_id !== currentUserId)
            .slice(0, 5)
            .map((a: any) => ({
              id: `a-${a.id}`,
              title: a.title,
              type: 'announcement' as const,
              time: 'Recently',
              creatorId: a.teacher_id
            })) : []),
          ...(Array.isArray(events) ? events
            .filter((e: any) => e.admin_id !== currentUserId)
            .slice(0, 5)
            .map((e: any) => ({
              id: `e-${e.id}`,
              title: e.title,
              type: 'event' as const,
              time: e.event_date || 'Upcoming',
              creatorId: e.admin_id
            })) : [])
        ];
        
        setNotifications(combined);
        if (combined.length > 0 && !localStorage.getItem('notificationsRead')) {
          setHasUnread(true);
        }
      } catch (error) {
        console.error('Failed to fetch notifications');
      }
    };

    if (user) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 60000);
      return () => clearInterval(interval);
    }
  }, [user, userRole]);

  const handleMarkAllRead = () => {
    setHasUnread(false);
    localStorage.setItem('notificationsRead', 'true');
    toast.success('All notifications marked as read');
  };

  const handleViewAll = () => {
    const path = userRole === 'admin' ? '/admin/events' : `/${userRole}/announcements`;
    navigate(path);
    setShowNotifications(false);
    setHasUnread(false);
    localStorage.setItem('notificationsRead', 'true');
  };

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
        className={`fixed lg:static inset-y-0 left-0 z-50 ${sidebarWidth} bg-white border-r border-gray-200 transition-all duration-500 ease-in-out flex flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo Section */}
        <div className="h-16 flex items-center px-6 border-b border-gray-100 relative overflow-hidden">
          <div className={`flex items-center gap-3 shrink-0`}>
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold shrink-0">L</div>
            <span className={`text-xl font-bold text-gray-900 tracking-tight truncate transition-all duration-500 ${sidebarCollapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>LMS Pro</span>
          </div>
          
          {/* Sidebar Toggle - Centered when collapsed, right-aligned when expanded */}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className={`p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-500 absolute top-1/2 -translate-y-1/2 ${sidebarCollapsed ? 'left-1/2 -translate-x-1/2' : 'right-4'}`}
            title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            <PanelLeft size={20} className={`transition-transform duration-500 ${sidebarCollapsed ? 'rotate-180' : ''}`} />
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
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl group ${
                  active
                    ? 'bg-primary-50 text-primary-700 font-semibold'
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                }`}
                title={sidebarCollapsed ? item.label : ''}
              >
                <Icon size={20} className={active ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'} />
                <span className={`text-sm transition-all duration-500 ${sidebarCollapsed ? 'opacity-0 w-0 pointer-events-none' : 'opacity-100'}`}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* User Profile Section */}
        <div className="p-4 border-t border-gray-100">
          <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'justify-center' : 'px-2 py-2'}`}>
            <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 border border-gray-200 shrink-0">
              <UserCircle size={24} />
            </div>
            <div className={`flex-1 min-w-0 transition-all duration-500 ${sidebarCollapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
              <p className="text-sm font-semibold text-gray-900 truncate">{user?.name || 'User'}</p>
              <p className="text-xs text-gray-500 capitalize">{userRole}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className={`mt-2 w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-500 hover:bg-red-50 ${sidebarCollapsed ? 'justify-center' : ''}`}
            title={sidebarCollapsed ? 'Logout' : ''}
          >
            <LogOut size={18} className="shrink-0" />
            <span className={`text-sm font-medium transition-all duration-500 ${sidebarCollapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
              Logout
            </span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-8 shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              <Menu size={24} />
            </button>
            <h1 className="text-lg font-semibold text-gray-900 capitalize">
              {location.pathname.split('/').pop()?.replace(/-/g, ' ') || 'Dashboard'}
            </h1>
          </div>

          <div className="flex items-center gap-2 lg:gap-4">
            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-colors relative"
              >
                <Bell size={22} />
                {hasUnread && (
                  <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full" />
                )}
              </button>

              {showNotifications && (
                <>
                  <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setShowNotifications(false)}
                  />
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden">
                    <div className="p-4 border-b border-gray-50 flex items-center justify-between bg-gray-50/50">
                      <h3 className="font-bold text-gray-900">Notifications</h3>
                      <button 
                        onClick={handleMarkAllRead}
                        className="text-xs font-medium text-primary-600 hover:text-primary-700"
                      >
                        Mark all read
                      </button>
                    </div>
                    <div className="max-h-[400px] overflow-y-auto">
                      {notifications.length > 0 ? (
                        notifications.map((notification) => (
                          <div 
                            key={notification.id}
                            className="p-4 hover:bg-gray-50 border-b border-gray-50 transition-colors cursor-pointer group"
                          >
                            <div className="flex gap-3">
                              <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                                notification.type === 'announcement' 
                                  ? 'bg-blue-50 text-blue-600' 
                                  : 'bg-purple-50 text-purple-600'
                              }`}>
                                {notification.type === 'announcement' ? <Bell size={18} /> : <Calendar size={18} />}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-1">
                                  {notification.title}
                                </p>
                                <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                                  <Clock size={12} />
                                  {notification.time}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="p-8 text-center">
                          <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
                            <Bell size={20} className="text-gray-400" />
                          </div>
                          <p className="text-sm text-gray-500">No new notifications</p>
                        </div>
                      )}
                    </div>
                    <div className="p-3 bg-gray-50/50 border-t border-gray-50">
                      <button 
                        onClick={handleViewAll}
                        className="w-full py-2 text-sm font-semibold text-gray-700 hover:text-primary-600 transition-colors"
                      >
                        View all updates
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="h-8 w-px bg-gray-200 mx-1 hidden sm:block" />

            <button
              onClick={() => setChatbotOpen(!chatbotOpen)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300 ${
                chatbotOpen 
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-200' 
                  : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
              }`}
            >
              <Sparkles size={18} className={chatbotOpen ? 'animate-pulse' : ''} />
              <span className="text-sm font-bold hidden sm:inline">AI Assistant</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8 relative">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
          
          {/* Chatbot Widget */}
          <ChatbotWidget 
            isOpen={chatbotOpen} 
            onClose={() => setChatbotOpen(false)} 
          />
        </div>
      </main>
    </div>
  );
};

export default Layout;
