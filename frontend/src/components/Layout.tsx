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
  MessageSquare,
} from 'lucide-react';
import Crest from './Crest';
import { getLatestAnnouncements, getEvents, getPublishedTimetableInfo, getAssignments, getSubmissionsByStudent, getClassTests, getExamTerms } from '../services/api';
import toast from 'react-hot-toast';

interface LayoutProps {
  children: React.ReactNode;
}

interface Notification {
  id: string | number;
  title: string;
  type: 'announcement' | 'event' | 'timetable' | 'assignment' | 'grade' | 'report';
  time: string;
  creatorId?: number | string;
  fromIncharge?: boolean;   // a class announcement from the class incharge (shown in amber)
  path?: string;            // the page it opens
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// "2026-11-05..." or "Thu, 05 Nov 2026 14:00:00 GMT" -> "5 Nov 2026" (read from the text,
// so no time zone can move it to another day)
const shortDate = (value: any): string => {
  const text = String(value || '');
  const iso = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) {
    return `${Number(iso[3])} ${MONTHS[Number(iso[2]) - 1]} ${iso[1]}`;
  }
  const rfc = text.match(/(\d{1,2}) ([A-Z][a-z]{2}) (\d{4})/);
  if (rfc) {
    return `${Number(rfc[1])} ${rfc[2]} ${rfc[3]}`;
  }
  return '';
};

// The ids of the notifications the user has already seen (saved in this browser)
const readSeenIds = (): string[] => {
  try {
    const saved = JSON.parse(localStorage.getItem('notificationsSeen') || '[]');
    return Array.isArray(saved) ? saved : [];
  } catch (error) {
    return [];
  }
};

// The list of a response: a plain list, or {"data": [...]}
const listOf = (data: any): any[] => {
  if (Array.isArray(data)) {
    return data;
  }
  if (data && Array.isArray(data.data)) {
    return data.data;
  }
  if (data && Array.isArray(data.assignments)) {
    return data.assignments;
  }
  return [];
};

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { logout, userRole, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // The slide-out menu (phones only; on a computer the menu is always shown).
  // It starts closed on every page load, so it never covers the page by itself.
  const [sidebarOpen, setSidebarOpen] = useState(false);
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

  // Moving to another page closes the notifications panel and the phone menu
  useEffect(() => {
    setShowNotifications(false);
    setSidebarOpen(false);
  }, [location.pathname]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [hasUnread, setHasUnread] = useState(false);


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
          // A few more than shown, since the user's own posts are left out below
          getLatestAnnouncements(15),
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
              time: shortDate(a.created_at) || 'Recently',
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
              time: shortDate(e.event_date) + (e.event_time ? ` · ${e.event_time}` : ''),
              creatorId: e.admin_id
            })) : [])
        ];
        
        // For students: new work, marks and report cards
        if (userRole === 'student') {
          const today = new Date().toLocaleDateString('en-CA');
          const [assignmentData, submissionData, testData, termData] = await Promise.all([
            getAssignments().catch(() => []),
            getSubmissionsByStudent().catch(() => []),
            getClassTests().catch(() => []),
            getExamTerms().catch(() => []),
          ]);
          const submissions = listOf(submissionData);

          // Assignments still to hand in
          for (const assignment of listOf(assignmentData)) {
            const handedIn = submissions.some((sub: any) => sub.assignment_id === assignment.id);
            if (!handedIn && String(assignment.due_date) >= today) {
              combined.push({
                id: `as-${assignment.id}`,
                title: `New assignment: ${assignment.title} (${assignment.subject_name})`,
                type: 'assignment',
                time: `Due ${shortDate(assignment.due_date)}`,
                path: '/student/assignments',
              });
            }
          }
          // Graded work
          for (const sub of submissions) {
            if (sub.marks !== null && sub.marks !== undefined) {
              combined.push({
                id: `gr-${sub.id}-${sub.marks}`,
                title: `${sub.assignment} has been graded: ${Number(sub.marks)} marks`,
                type: 'grade',
                time: 'Assignment',
                path: '/student/assignments',
              });
            }
          }
          // Class test marks
          for (const test of listOf(testData)) {
            if (test.my_marks !== null && test.my_marks !== undefined) {
              combined.push({
                id: `ct-${test.id}-${test.my_marks}`,
                title: `${test.title}: ${test.my_marks} / ${Number(test.total_marks)}`,
                type: 'grade',
                time: 'Class test',
                path: '/student/class-tests',
              });
            }
          }
          // Published report cards (students only get published terms)
          for (const term of listOf(termData)) {
            combined.push({
              id: `rc-${term.id}`,
              title: `Your ${term.name} report card is ready`,
              type: 'report',
              time: term.session_name || '',
              path: '/student/report-card',
            });
          }
        }

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
        // The red dot shows while there is anything the user hasn't seen yet
        const seen = readSeenIds();
        const somethingNew = combined.some((n) => n.type !== 'timetable' && !seen.includes(String(n.id)));
        setHasUnread(somethingNew || newTimetable);
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

  // The icon colour in the bell: class incharge announcements in amber, like on the pages;
  // school announcements in green, everything else plain
  const notificationColour = (n: Notification): string => {
    if (n.type === 'announcement' && n.fromIncharge) {
      return 'bg-amber-50 text-amber-700';
    }
    if (n.type === 'announcement') {
      return 'bg-primary-50 text-primary-700';
    }
    return 'bg-gray-100 text-gray-700';
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
    // Remember every notification shown now; only newer ones light up the bell again
    const ids: string[] = [];
    for (const n of notifications) {
      ids.push(String(n.id));
    }
    localStorage.setItem('notificationsSeen', JSON.stringify(ids));
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
    // Every real page is named above, so anything else is an unknown address
    return 'Page not found';
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
  const sidebarWidth = collapsed ? 'w-[4.5rem]' : 'w-60';

  // "Classes / Section" -> "Classes" in grey, then "Section"
  const titleParts = pageTitle().split(' / ');

  return (
    <div className="min-h-screen bg-gray-50 flex overflow-hidden">
      {/* Phone menu backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900/40 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* The menu: the green cover of the register. The open page shows as a paper
          index tab that runs into the page. */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 ${sidebarWidth} bg-primary-800 text-primary-100 transition-[width,transform] duration-200 ease-out flex flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Name of the school */}
        <div className={`h-16 flex items-center shrink-0 ${collapsed ? 'justify-center px-2' : 'px-5'}`}>
          {!collapsed ? (
            <div className="flex items-center gap-2.5 w-full min-w-0">
              <Crest size={30} className="shrink-0" />
              <span className="font-serif text-[1.3rem] font-semibold text-white tracking-tight truncate">The Lyceum</span>
              <button
                onClick={() => setSidebarCollapsed(true)}
                className="hidden lg:flex ml-auto p-1.5 text-primary-300 hover:text-white hover:bg-white/10 rounded-md transition-colors"
                title="Collapse menu"
                aria-label="Collapse menu"
              >
                <PanelLeft size={17} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setSidebarCollapsed(false)}
              className="p-1 rounded-md hover:bg-white/10 transition-colors"
              title="Expand menu"
              aria-label="Expand menu"
            >
              <Crest size={30} />
            </button>
          )}

          <button
            onClick={() => setSidebarOpen(false)}
            title="Close menu"
            aria-label="Close menu"
            className="lg:hidden ml-auto p-2 text-primary-200 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Menu */}
        <nav className="flex-1 overflow-y-auto py-3 pl-3 space-y-0.5" aria-label="Main menu">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                aria-current={active ? 'page' : undefined}
                className={`flex items-center gap-3 py-2 text-sm transition-colors ${
                  collapsed ? 'justify-center pr-3' : 'px-3'
                } ${
                  active
                    ? 'bg-gray-50 text-primary-800 font-semibold rounded-l-md lg:mr-0 mr-3 lg:rounded-r-none rounded-r-md'
                    : 'mr-3 rounded-md text-primary-100/85 hover:bg-white/10 hover:text-white'
                }`}
                title={collapsed ? item.label : ''}
              >
                <Icon size={18} strokeWidth={active ? 2.2 : 1.8} className={active ? 'text-primary-600' : 'text-primary-300'} />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Who is logged in */}
        <div className="px-3 py-4 border-t border-white/10">
          <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : 'px-2'}`}>
            <div className="w-9 h-9 rounded-full bg-primary-700 text-primary-100 flex items-center justify-center text-sm font-semibold shrink-0" aria-hidden="true">
              {(user?.name || 'U').trim().charAt(0).toUpperCase()}
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-primary-300 capitalize">{userRole}</p>
              </div>
            )}
          </div>
          <div className={`mt-3 flex ${collapsed ? 'flex-col items-center gap-1' : 'gap-1'}`}>
            <Link
              to="/account"
              className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors ${
                isActive('/account') ? 'bg-white/15 text-white' : 'text-primary-200 hover:bg-white/10 hover:text-white'
              }`}
              title="My Account"
            >
              <Settings size={16} />
              {!collapsed && <span>My Account</span>}
            </Link>
            <button
              onClick={handleLogout}
              className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-sm text-primary-200 hover:bg-white/10 hover:text-white transition-colors ${collapsed ? '' : 'ml-auto'}`}
              title="Log out"
            >
              <LogOut size={16} />
              {!collapsed && <span>Log out</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Page */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Top bar */}
        <header className="h-16 bg-gray-50 border-b border-gray-200 flex items-center justify-between px-4 lg:px-8 shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => setSidebarOpen(true)}
              title="Open menu"
              aria-label="Open menu"
              className="lg:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-md"
            >
              <Menu size={20} />
            </button>
            <p className="text-sm truncate">
              {titleParts.map((part, index) => (
                <span key={index}>
                  {index > 0 && <span className="text-gray-400 mx-1.5">/</span>}
                  <span className={index === titleParts.length - 1 ? 'font-semibold text-gray-900' : 'text-gray-500'}>{part}</span>
                </span>
              ))}
            </p>
          </div>

          <div className="flex items-center gap-1">
            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                title="Notifications"
                aria-label="Notifications"
                aria-expanded={showNotifications}
                className={`p-2.5 rounded-md transition-colors relative ${
                  showNotifications ? 'bg-gray-200 text-gray-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Bell size={19} />
                {hasUnread && (
                  <span className="absolute top-2 right-2 w-2 h-2 bg-red-600 rounded-full ring-2 ring-gray-50"></span>
                )}
              </button>

              {showNotifications && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)}></div>
                  <div className="absolute right-0 mt-2 w-[22rem] max-w-[calc(100vw-2rem)] bg-white border border-gray-300 rounded-lg shadow-[0_8px_24px_-8px_rgba(28,27,24,0.25)] z-20 overflow-hidden">
                    <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">Notifications</h3>
                      <button
                        onClick={handleMarkAllRead}
                        className="text-xs text-primary-700 font-medium hover:underline"
                      >
                        Mark all as read
                      </button>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.length > 0 ? (
                        <div className="divide-y divide-gray-100">
                          {notifications.map((n) => (
                            <button
                              type="button"
                              key={n.id}
                              className="block w-full text-left px-4 py-3 hover:bg-gray-50 focus-visible:bg-gray-50 transition-colors"
                              onClick={() => {
                                setShowNotifications(false);
                                // This one is now seen
                                const seen = readSeenIds();
                                if (!seen.includes(String(n.id))) {
                                  seen.push(String(n.id));
                                  localStorage.setItem('notificationsSeen', JSON.stringify(seen));
                                }
                                // The timetable notice opens the Timetable page
                                if (n.type === 'timetable') {
                                  markTimetableSeen();
                                  setHasUnread(false);
                                  navigate(`/${userRole}/timetable`);
                                } else if (n.path) {
                                  navigate(n.path);
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
                                <div className={`mt-0.5 p-1.5 rounded-md ${notificationColour(n)}`}>
                                  {n.type === 'announcement' ? <Bell size={14} /> : n.type === 'timetable' ? <CalendarDays size={14} /> : n.type === 'event' ? <Calendar size={14} /> : n.type === 'report' ? <Award size={14} /> : <FileText size={14} />}
                                </div>
                                <div>
                                  <p className="text-sm text-gray-900">{n.title}</p>
                                  <p className="text-xs text-gray-500 mt-0.5">{n.time}</p>
                                </div>
                              </div>
                            </button>
                          ))}
                        </div>
                      ) : (
                        <p className="px-4 py-8 text-center text-gray-500 text-sm">Nothing new.</p>
                      )}
                    </div>
                    <div className="px-4 py-2.5 bg-gray-50 border-t border-gray-200">
                      <button
                        onClick={handleViewAll}
                        className="text-sm font-medium text-primary-700 hover:underline"
                      >
                        All announcements
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* The assistant */}
            <button
              onClick={() => setChatbotOpen(!chatbotOpen)}
              className={`flex items-center gap-2 px-2.5 py-2 rounded-md text-sm transition-colors ${
                chatbotOpen ? 'bg-primary-600 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              title="Assistant"
              aria-label="Assistant"
              aria-expanded={chatbotOpen}
            >
              <MessageSquare size={19} />
              <span className="hidden sm:inline font-medium">Assistant</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8">
          {children}
        </div>

        <ChatbotWidget
          isOpen={chatbotOpen}
          onClose={() => setChatbotOpen(false)}
        />
      </main>
    </div>
  );
};
