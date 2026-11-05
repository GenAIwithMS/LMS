import React, { useState, useEffect } from 'react';
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
  LogOut,
  Menu,
  X,
  UserCircle,
  Settings,
  ClipboardList,
  Award,
  Clock,
  PanelLeft,
  ClipboardCheck,
  TrendingUp,
  Eye,
  History,
  FileSpreadsheet,
  CalendarDays,
  Megaphone,
} from 'lucide-react';
import { getAnnouncements, getEvents, getPublishedTimetableInfo } from '../services/api';
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
  type: 'announcement' | 'event' | 'timetable';
  time: string;
  creatorId?: number | string;
  fromIncharge?: boolean;   // a class announcement from the class incharge (shown in amber)
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
  // Collapsing the menu to icons is only for wide screens. On a phone the menu slides out
  // over the page, so it always shows the labels.
  const [isWideScreen, setIsWideScreen] = useState(() => window.matchMedia('(min-width: 1024px)').matches);
  useEffect(() => {
    const query = window.matchMedia('(min-width: 1024px)');
    const handleChange = () => setIsWideScreen(query.matches);
    query.addEventListener('change', handleChange);
    return () => query.removeEventListener('change', handleChange);
  }, []);
  const [chatbotOpen, setChatbotOpen] = useState(() => {
    const saved = localStorage.getItem('chatbotOpen');
    return saved !== null ? saved === 'true' : false;
  });
  const [showNotifications, setShowNotifications] = useState(false);

  // Moving to another page closes the notifications panel
  useEffect(() => {
    setShowNotifications(false);
  }, [location.pathname]);
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
        
        // Hide the user's own posts: a teacher's own announcements and the admin's
        // own events. The id in the login is text, so turn it into a number first,
        // and check the role too (a teacher and the admin can have the same id).
        const currentUserId = Number(user?.id);

        const combined: Notification[] = [
          ...(Array.isArray(announcements) ? announcements
            .filter((a: any) => !(userRole === 'teacher' && a.teacher_id === currentUserId) && !(userRole === 'admin' && a.admin_id === currentUserId))
            .slice(0, 5)
            .map((a: any) => ({
              id: `a-${a.id}`,
              title: a.title,
              type: 'announcement' as const,
              time: 'Recently',
              creatorId: a.teacher_id,
              fromIncharge: a.from_incharge === true
            })) : []),
          ...(Array.isArray(events) ? events
            .filter((e: any) => !(userRole === 'admin' && e.admin_id === currentUserId))
            // Only events from today onwards; past events are no longer news
            .filter((e: any) => String(e.event_date || '').slice(0, 10) >= new Date().toLocaleDateString('en-CA'))
            .slice(0, 5)
            .map((e: any) => ({
              id: `e-${e.id}`,
              title: e.title,
              type: 'event' as const,
              time: e.event_date || 'Upcoming',
              creatorId: e.admin_id
            })) : [])
        ];
        
        // A newly published timetable, for teachers and students
        let newTimetable = false;
        if (userRole === 'teacher' || userRole === 'student') {
          const timetableInfo = await getPublishedTimetableInfo();
          if (timetableInfo.is_published) {
            combined.unshift({
              id: `t-${timetableInfo.version_id}`,
              title: 'The timetable has been published. Open it to see your week.',
              type: 'timetable',
              time: timetableInfo.published_at,
            });
            // The bell lights up again for every new version
            if (localStorage.getItem('timetableSeenVersion') !== String(timetableInfo.version_id)) {
              newTimetable = true;
              localStorage.setItem('timetableLatestVersion', String(timetableInfo.version_id));
            }
          }
        }

        setNotifications(combined);
        if ((combined.length > 0 && !localStorage.getItem('notificationsRead')) || newTimetable) {
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

  // The icon colour in the bell: class incharge announcements in amber, like on the pages
  const notificationColour = (n: Notification): string => {
    if (n.type === 'announcement' && n.fromIncharge) {
      return 'bg-amber-50 text-amber-600';
    }
    if (n.type === 'announcement') {
      return 'bg-blue-50 text-blue-600';
    }
    if (n.type === 'timetable') {
      return 'bg-green-50 text-green-600';
    }
    return 'bg-purple-50 text-purple-600';
  };

  // Remember the newest timetable as seen, so the bell stays quiet until the next one
  const markTimetableSeen = () => {
    const latest = localStorage.getItem('timetableLatestVersion');
    if (latest) {
      localStorage.setItem('timetableSeenVersion', latest);
    }
  };

  const handleMarkAllRead = () => {
    setHasUnread(false);
    markTimetableSeen();
    localStorage.setItem('notificationsRead', 'true');
    toast.success('All notifications marked as read');
  };

  const handleViewAll = () => {
    // Notifications are mostly announcements, so "View all" opens the announcements page
    const path = `/${userRole}/announcements`;
    navigate(path);
    setShowNotifications(false);
    setHasUnread(false);
    localStorage.setItem('notificationsRead', 'true');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    if (location.pathname === path) {
      return true;
    }
    // The class and section pages belong to "Classes" / "My Classes"
    if (path === '/admin/classes' && location.pathname.startsWith('/admin/')) {
      return location.pathname.startsWith('/admin/classes/') || location.pathname.startsWith('/admin/sections/');
    }
    // A teacher's activity page belongs to "Teachers"
    if (path === '/admin/teachers') {
      return location.pathname.startsWith('/admin/teachers/');
    }
    // A term's page and the grading scale belong to "Exams"
    if (path === '/admin/exams') {
      return location.pathname.startsWith('/admin/exams/') || location.pathname === '/admin/grading';
    }
    if (path === '/teacher/classes') {
      return location.pathname.startsWith('/teacher/sections/');
    }
    return false;
  };

  const adminMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/admin/oversight', label: 'Oversight', icon: Eye },
    { path: '/admin/classes', label: 'Classes', icon: BookOpen },
    { path: '/admin/timetable', label: 'Timetable', icon: CalendarDays },
    { path: '/admin/students', label: 'Students', icon: Users },
    { path: '/admin/teachers', label: 'Teachers', icon: GraduationCap },
    { path: '/admin/exams', label: 'Exams', icon: Award },
    { path: '/admin/promotion', label: 'Promotion', icon: TrendingUp },
    { path: '/admin/activity', label: 'Activity Log', icon: History },
    { path: '/admin/reports', label: 'Reports', icon: FileSpreadsheet },
    { path: '/admin/announcements', label: 'Announcements', icon: Megaphone },
    { path: '/admin/events', label: 'Events', icon: Calendar },
  ];

  const teacherMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/teacher/classes', label: 'My Classes', icon: BookOpen },
    { path: '/teacher/timetable', label: 'Timetable', icon: CalendarDays },
    { path: '/teacher/assignments', label: 'Assignments', icon: FileText },
    { path: '/teacher/attendance', label: 'Attendance', icon: Clock },
    { path: '/teacher/exams', label: 'Exams', icon: Award },
    { path: '/teacher/class-tests', label: 'Class Tests', icon: ClipboardCheck },
    { path: '/teacher/announcements', label: 'Announcements', icon: Bell },
    { path: '/teacher/submissions', label: 'Submissions', icon: ClipboardList },
  ];

  const studentMenuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/student/class', label: 'My Class', icon: BookOpen },
    { path: '/student/timetable', label: 'Timetable', icon: CalendarDays },
    { path: '/student/assignments', label: 'Assignments', icon: FileText },
    { path: '/student/report-card', label: 'Report Card', icon: Award },
    { path: '/student/class-tests', label: 'Class Tests', icon: ClipboardCheck },
    { path: '/student/attendance', label: 'Attendance', icon: Clock },
    { path: '/student/announcements', label: 'Announcements', icon: Bell },
  ];

  const menuItems = userRole === 'admin' ? adminMenuItems : userRole === 'teacher' ? teacherMenuItems : studentMenuItems;

  // The title in the top bar: the menu item's name, or a readable name for pages inside one
  // (no raw addresses or ID numbers)
  const pageTitle = (): string => {
    const path = location.pathname;
    for (const item of menuItems) {
      if (item.path === path) {
        return item.label;
      }
    }
    let match = path.match(/^\/admin\/classes\/(\d+)$/);
    if (match) {
      return `Classes / Class ${match[1]}`;
    }
    if (/^\/admin\/sections\/\d+$/.test(path)) {
      return 'Classes / Section';
    }
    if (/^\/teacher\/sections\/\d+$/.test(path)) {
      return 'My Classes / Section';
    }
    if (/^\/admin\/teachers\/\d+\/activity$/.test(path)) {
      return 'Teachers / Teacher activity';
    }
    if (/^\/admin\/exams\/\d+$/.test(path)) {
      return 'Exams / Exam term';
    }
    if (path === '/admin/grading') {
      return 'Exams / Grading scale';
    }
    if (path.startsWith('/report-card/')) {
      return 'Report card';
    }
    if (path === '/account') {
      return 'My Account';
    }
    if (path === '/chatbot') {
      return 'Assistant';
    }
    // Anything else: the last part of the address, as words
    const parts = path.split('/').filter((part) => part !== '' && !/^\d+$/.test(part));
    if (parts.length === 0) {
      return 'Dashboard';
    }
    const last = parts[parts.length - 1].replace(/-/g, ' ');
    return last.charAt(0).toUpperCase() + last.slice(1);
  };

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

  const collapsed = sidebarCollapsed && isWideScreen;
  const sidebarWidth = collapsed ? 'w-20' : 'w-64';

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
        <div className="h-16 flex items-center px-6 border-b border-gray-100 relative overflow-hidden bg-gradient-to-r from-primary-50/30 to-transparent">
          {!collapsed ? (
            <div className="flex items-center gap-3 shrink-0 w-full">
              <div className="w-9 h-9 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center text-white font-bold shrink-0 shadow-lg">
                L
              </div>
              <span className="text-xl font-bold text-gray-900 tracking-tight truncate">LMS Pro</span>
              <button
                onClick={() => setSidebarCollapsed(true)}
                className="hidden lg:block ml-auto p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all"
                title="Collapse Sidebar"
              >
                <PanelLeft size={18} />
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-center w-full">
              <button
                onClick={() => setSidebarCollapsed(false)}
                className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all"
                title="Expand Sidebar"
              >
                <PanelLeft size={18} className="rotate-180" />
              </button>
            </div>
          )}

          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden ml-auto text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative overflow-hidden ${
                  active
                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold shadow-lg shadow-primary-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
                title={collapsed ? item.label : ''}
              >
                {active && (
                  <div className="absolute inset-0 bg-white/10 animate-shimmer"></div>
                )}
                <Icon size={20} className={`relative z-10 ${active ? 'text-white' : 'text-gray-400 group-hover:text-gray-600'}`} />
                {!collapsed && <span className="text-sm relative z-10">{item.label}</span>}
                {active && !collapsed && (
                  <div className="ml-auto w-1.5 h-1.5 bg-white rounded-full relative z-10"></div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Profile Section */}
        <div className="p-4 border-t border-gray-100 bg-gray-50/50">
          <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : 'px-2 py-2'}`}>
            <div className="w-10 h-10 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center text-primary-700 border-2 border-primary-300 shadow-md">
              <UserCircle size={24} />
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-gray-900 truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500 capitalize font-medium">{userRole}</p>
              </div>
            )}
          </div>
          <Link
            to="/account"
            className={`mt-3 w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all font-semibold shadow-sm hover:shadow-md ${
              isActive('/account') ? 'bg-primary-100 text-primary-700' : 'text-gray-700 bg-white hover:bg-gray-100'
            } ${collapsed ? 'justify-center' : ''}`}
            title={collapsed ? 'My Account' : ''}
          >
            <Settings size={18} />
            {!collapsed && <span className="text-sm">My Account</span>}
          </Link>
          <button
            onClick={handleLogout}
            className={`mt-3 w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-red-600 bg-red-50 hover:bg-red-100 transition-all font-semibold shadow-sm hover:shadow-md ${collapsed ? 'justify-center' : ''}`}
            title={collapsed ? 'Logout' : ''}
          >
            <LogOut size={18} />
            {!collapsed && <span className="text-sm">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-8 shrink-0 shadow-sm">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              title="Open menu"
              aria-label="Open menu"
              className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-xl transition-all"
            >
              <Menu size={20} />
            </button>
            <div className="hidden lg:block">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                <h2 className="text-sm font-bold text-gray-800">
                  {pageTitle()}
                </h2>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Notification Icon */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                title="Notifications"
                aria-label="Notifications"
                className={`p-2.5 rounded-xl transition-all relative ${
                  showNotifications 
                    ? 'bg-primary-50 text-primary-600 shadow-md' 
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Bell size={20} />
                {hasUnread && (
                  <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white animate-pulse"></span>
                )}
              </button>
              
              {/* Notification Dropdown */}
              {showNotifications && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)}></div>
                  <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-xl z-20 overflow-hidden animate-in fade-in zoom-in duration-200">
                    <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                      <h3 className="font-bold text-gray-900">Notifications</h3>
                      <button 
                        onClick={handleMarkAllRead}
                        className="text-xs text-primary-600 font-medium hover:underline"
                      >
                        Mark all as read
                      </button>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.length > 0 ? (
                        <div className="divide-y divide-gray-50">
                          {notifications.map((n) => (
                            <div
                              key={n.id}
                              className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                              onClick={() => {
                                setShowNotifications(false);
                                // The timetable notice opens the Timetable page
                                if (n.type === 'timetable') {
                                  markTimetableSeen();
                                  setHasUnread(false);
                                  navigate(`/${userRole}/timetable`);
                                } else if (n.type === 'announcement') {
                                  navigate(`/${userRole}/announcements`);
                                } else if (userRole === 'admin') {
                                  navigate('/admin/events');
                                } else {
                                  // Teachers and students see the upcoming events on the dashboard
                                  navigate('/dashboard');
                                }
                              }}
                            >
                              <div className="flex items-start gap-3">
                                <div className={`mt-1 p-1.5 rounded-lg ${notificationColour(n)}`}>
                                  {n.type === 'announcement' ? <Bell size={14} /> : n.type === 'timetable' ? <CalendarDays size={14} /> : <Calendar size={14} />}
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{n.title}</p>
                                  <p className="text-[10px] text-gray-400 mt-1 uppercase font-bold tracking-wider">{n.time}</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="p-8 text-center text-gray-500 text-sm">
                          <Bell size={32} className="mx-auto text-gray-200 mb-2" />
                          <p>No new notifications</p>
                        </div>
                      )}
                    </div>
                    <div className="p-3 bg-gray-50 border-t border-gray-100 text-center">
                      <button 
                        onClick={handleViewAll}
                        className="text-xs font-bold text-gray-500 hover:text-gray-700 uppercase tracking-wider"
                      >
                        View All Announcements
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="h-8 w-px bg-gray-200 mx-1"></div>
            
            {/* Manus Assistant Icon */}
            <button 
              onClick={() => setChatbotOpen(!chatbotOpen)}
              className={`p-2.5 rounded-xl transition-all ${
                chatbotOpen 
                  ? 'bg-indigo-50 text-indigo-600 ring-2 ring-indigo-200 shadow-md' 
                  : 'text-gray-400 hover:text-indigo-600 hover:bg-indigo-50'
              }`}
              title="Manus Assistant"
            >
              <ManusIcon size={20} />
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
