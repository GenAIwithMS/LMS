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
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { logout, userRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(256); // 64 * 4 = 256px (w-64)
  const [isResizing, setIsResizing] = useState(false);
  const [chatbotOpen, setChatbotOpen] = useState(true);
  const [chatbotWidth, setChatbotWidth] = useState(400);
  const [chatbotCollapsed, setChatbotCollapsed] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const resizeStartRef = useRef<{ x: number; width: number } | null>(null);

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

  // Handle sidebar resize
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing && resizeStartRef.current) {
        const deltaX = e.clientX - resizeStartRef.current.x; // Normal direction for left sidebar
        const newWidth = Math.max(200, Math.min(400, resizeStartRef.current.width + deltaX));
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      resizeStartRef.current = null;
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    resizeStartRef.current = {
      x: e.clientX,
      width: sidebarWidth,
    };
  };

  const displayWidth = sidebarCollapsed ? 64 : sidebarWidth; // Show 64px (icon width) when collapsed

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Navigation Sidebar - Left */}
      <aside
        ref={sidebarRef}
        className={`fixed top-0 left-0 z-50 h-full bg-white shadow-lg transition-all duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: `${displayWidth}px` }}
      >
        <div className="flex flex-col h-full relative">
          {/* Resize Handle */}
          {!sidebarCollapsed && (
            <div
              className="absolute right-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-primary-200 bg-transparent transition-colors z-10"
              onMouseDown={handleResizeStart}
            />
          )}

          {/* Collapse Toggle Button */}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="absolute -right-4 top-4 bg-white rounded-full p-1 shadow-md hover:bg-gray-100 transition-colors z-20 border border-gray-200"
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? (
              <ChevronRight size={20} className="text-gray-600" />
            ) : (
              <ChevronLeft size={20} className="text-gray-600" />
            )}
          </button>

          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b">
            {!sidebarCollapsed && <h1 className="text-2xl font-bold text-primary-600">LMS</h1>}
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <X size={24} />
            </button>
          </div>

          {/* Navigation */}
          {!sidebarCollapsed && (
            <>
              <nav className="flex-1 overflow-y-auto p-4">
                <ul className="space-y-2">
                  {menuItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <li key={item.path}>
                        <Link
                          to={item.path}
                          onClick={() => setSidebarOpen(false)}
                          className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                            isActive(item.path)
                              ? 'bg-primary-100 text-primary-700 font-medium'
                              : 'text-gray-700 hover:bg-gray-100'
                          }`}
                        >
                          <Icon size={20} />
                          <span>{item.label}</span>
                        </Link>
                      </li>
                    );
                  })}
                  {/* Chatbot Toggle */}
                  <li>
                    <button
                      onClick={() => {
                        setChatbotOpen(!chatbotOpen);
                        setSidebarOpen(false);
                      }}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                        chatbotOpen
                          ? 'bg-primary-100 text-primary-700 font-medium'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <MessageSquare size={20} />
                      <span>Chatbot</span>
                    </button>
                  </li>
                </ul>
              </nav>

              {/* User section */}
              <div className="p-4 border-t">
                <div className="flex items-center space-x-3 mb-3 px-4 py-2">
                  <UserCircle size={24} className="text-gray-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-700">
                      {userRole ? userRole.charAt(0).toUpperCase() + userRole.slice(1) : 'User'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                >
                  <LogOut size={20} />
                  <span>Logout</span>
                </button>
              </div>
            </>
          )}

          {/* Collapsed Sidebar - Show only icons */}
          {sidebarCollapsed && (
            <nav className="flex-1 overflow-y-auto p-2">
              <ul className="space-y-2">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <li key={item.path}>
                      <Link
                        to={item.path}
                        onClick={() => setSidebarOpen(false)}
                        className={`flex items-center justify-center p-3 rounded-lg transition-colors ${
                          isActive(item.path)
                            ? 'bg-primary-100 text-primary-700'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                        title={item.label}
                      >
                        <Icon size={20} />
                      </Link>
                    </li>
                  );
                })}
                <li>
                  <button
                    onClick={() => {
                      setChatbotOpen(!chatbotOpen);
                      setSidebarOpen(false);
                    }}
                    className={`w-full flex items-center justify-center p-3 rounded-lg transition-colors ${
                      chatbotOpen
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Chatbot"
                  >
                    <MessageSquare size={20} />
                  </button>
                </li>
                <li>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center p-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                    title="Logout"
                  >
                    <LogOut size={20} />
                  </button>
                </li>
              </ul>
            </nav>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div 
        style={{ 
          marginLeft: `${displayWidth}px`,
          marginRight: chatbotOpen ? (chatbotCollapsed ? '64px' : `${chatbotWidth}px`) : '0px'
        }} 
        className="transition-all duration-300"
      >
        {/* Top bar */}
        <header className="bg-white shadow-sm sticky top-0 z-30">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <Menu size={24} />
            </button>
            <div className="flex-1" />
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>

      {/* Chatbot Sidebar - Right */}
      <ChatbotWidget 
        isOpen={chatbotOpen} 
        onClose={() => setChatbotOpen(false)}
        onWidthChange={setChatbotWidth}
        onCollapseChange={setChatbotCollapsed}
      />
    </div>
  );
};

