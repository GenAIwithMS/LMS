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
  Award,
  ArrowRight,
  Clock,
} from 'lucide-react';
import { getStudents, getTeachers, getSchoolClasses, getAssignments, getAnnouncements, getEvents, getMyDailyAttendance, getSubmissionsByStudent } from '../services/api';
import toast from 'react-hot-toast';

// Count the rows in an API answer: a plain list, or a list inside "data" / "assignments"
const countRows = (data: any): number => {
  if (Array.isArray(data)) {
    return data.length;
  }
  if (data && Array.isArray(data.data)) {
    return data.data.length;
  }
  if (data && Array.isArray(data.assignments)) {
    return data.assignments.length;
  }
  return 0;
};

// Run one request and count its rows; a failed request counts as 0
const countFrom = async (request: () => Promise<any>): Promise<number> => {
  try {
    const data = await request();
    return countRows(data);
  } catch (error) {
    return 0;
  }
};

interface UpcomingEvent {
  id: number;
  title: string;
  event_date: string;
  event_time: string | null;
}

// The events from today onwards (past events are not "upcoming"), soonest first
const loadUpcomingEvents = async (): Promise<UpcomingEvent[]> => {
  try {
    const data = await getEvents();
    let events: any[] = [];
    if (Array.isArray(data)) {
      events = data;
    } else if (data && Array.isArray(data.data)) {
      events = data.data;
    }
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const today = `${now.getFullYear()}-${month}-${day}`;
    const upcoming: UpcomingEvent[] = [];
    for (const event of events) {
      const eventDate = String(event.event_date || '').slice(0, 10);
      if (eventDate >= today) {
        upcoming.push({ id: event.id, title: event.title, event_date: eventDate, event_time: event.event_time || null });
      }
    }
    upcoming.sort((a, b) => (a.event_date + (a.event_time || '')).localeCompare(b.event_date + (b.event_time || '')));
    return upcoming;
  } catch (error) {
    return [];
  }
};

const Dashboard: React.FC = () => {
  const { userRole, user } = useAuth();
  const navigate = useNavigate();
  const [upcomingEvents, setUpcomingEvents] = useState<UpcomingEvent[]>([]);
  const [stats, setStats] = useState({
    students: 0,
    teachers: 0,
    courses: 0,
    assignments: 0,
    announcements: 0,
    events: 0,
  });
  // Student only: attendance percentage ("-" before any day is marked) and work still to hand in
  const [myAttendance, setMyAttendance] = useState('-');
  const [toHandIn, setToHandIn] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        // Only ask for what this role is allowed to see. The server already limits
        // teachers and students to their own records, so the counts are theirs.
        const newStats = { students: 0, teachers: 0, courses: 0, assignments: 0, announcements: 0, events: 0 };

        if (userRole === 'admin') {
          newStats.students = await countFrom(getStudents);
          newStats.teachers = await countFrom(getTeachers);
          // "courses" now counts the sections of Classes 1-10
          try {
            const classes = await getSchoolClasses();
            let sectionCount = 0;
            for (const schoolClass of classes) {
              sectionCount = sectionCount + schoolClass.sections.length;
            }
            newStats.courses = sectionCount;
          } catch (error) {
            newStats.courses = 0;
          }
        }
        if (userRole === 'teacher') {
          newStats.students = await countFrom(getStudents);
        }
        newStats.assignments = await countFrom(getAssignments);

        if (userRole === 'student') {
          await loadStudentSummary();
        }
        newStats.announcements = await countFrom(getAnnouncements);
        const upcoming = await loadUpcomingEvents();
        setUpcomingEvents(upcoming);
        newStats.events = upcoming.length;

        setStats(newStats);
      } catch (error) {
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    // A student's attendance percentage, and the assignments not yet handed in that are still open
    const loadStudentSummary = async () => {
      try {
        const attendance = await getMyDailyAttendance();
        if (attendance && attendance.summary && attendance.summary.percentage !== null) {
          setMyAttendance(`${attendance.summary.percentage}%`);
        }
      } catch (error) {
        setMyAttendance('-');
      }
      try {
        const assignmentData = await getAssignments();
        const submissionData = await getSubmissionsByStudent();
        let assignments: any[] = [];
        if (Array.isArray(assignmentData)) {
          assignments = assignmentData;
        } else if (assignmentData && Array.isArray(assignmentData.assignments)) {
          assignments = assignmentData.assignments;
        } else if (assignmentData && Array.isArray(assignmentData.data)) {
          assignments = assignmentData.data;
        }
        let submissions: any[] = [];
        if (Array.isArray(submissionData)) {
          submissions = submissionData;
        } else if (submissionData && Array.isArray(submissionData.data)) {
          submissions = submissionData.data;
        }
        const today = new Date().toLocaleDateString('en-CA');
        let count = 0;
        for (const assignment of assignments) {
          const handedIn = submissions.some((sub) => sub.assignment_id === assignment.id);
          if (!handedIn && String(assignment.due_date) >= today) {
            count = count + 1;
          }
        }
        setToHandIn(count);
      } catch (error) {
        setToHandIn(0);
      }
    };

    fetchStats();
  }, [userRole]);

  const allStatCards = [
    {
      roles: ['admin', 'teacher'],
      title: userRole === 'teacher' ? 'My students' : 'Students',
      value: stats.students,
      path: userRole === 'admin' ? '/admin/students' : undefined,
    },
    {
      roles: ['admin'],
      title: 'Teachers',
      value: stats.teachers,
      path: '/admin/teachers',
    },
    {
      roles: ['admin'],
      title: 'Sections',
      value: stats.courses,
      path: '/admin/classes',
    },
    {
      roles: ['admin', 'teacher', 'student'],
      title: userRole === 'admin' ? 'Assignments set' : 'My assignments',
      value: stats.assignments,
      // The admin sees each teacher's assignments on the Oversight page
      path: userRole === 'teacher' ? '/teacher/assignments' : userRole === 'student' ? '/student/assignments' : '/admin/oversight',
    },
    {
      roles: ['student'],
      title: 'To hand in',
      value: toHandIn,
      path: '/student/assignments',
    },
    {
      roles: ['student'],
      title: 'My attendance',
      value: myAttendance,
      path: '/student/attendance',
    },
  ];

  // Each role only sees the figures that make sense for it
  const statCards = allStatCards.filter((card) => userRole !== null && card.roles.includes(userRole));

  // The shortcuts for each role: the things people do most often
  const adminShortcuts = [
    { label: 'Students', note: 'Add, edit and move students', path: '/admin/students', icon: Users },
    { label: 'Teachers', note: 'Staff and the subjects they teach', path: '/admin/teachers', icon: GraduationCap },
    { label: 'Classes', note: 'Sections, subjects and class incharges', path: '/admin/classes', icon: BookOpen },
    { label: 'Events', note: 'Holidays, meetings and school days', path: '/admin/events', icon: Calendar },
  ];
  const teacherShortcuts = [
    { label: 'Mark attendance', note: "Today's register for your class", path: '/teacher/attendance', icon: Clock },
    { label: 'Set an assignment', note: 'Homework with a due date', path: '/teacher/assignments', icon: FileText },
    { label: 'Enter exam marks', note: 'Marks for the current term', path: '/teacher/exams', icon: Award },
    { label: 'Post an announcement', note: 'To your classes', path: '/teacher/announcements', icon: Bell },
  ];
  const studentShortcuts = [
    { label: 'Assignments', note: 'What to hand in and when', path: '/student/assignments', icon: FileText },
    { label: 'Report card', note: 'Your marks for each term', path: '/student/report-card', icon: Award },
    { label: 'Attendance', note: 'Days present and absent', path: '/student/attendance', icon: Clock },
    { label: 'Announcements', note: 'From the school and your teachers', path: '/student/announcements', icon: Bell },
  ];
  const shortcuts = userRole === 'admin' ? adminShortcuts : userRole === 'teacher' ? teacherShortcuts : studentShortcuts;

  // "Good morning" before 12, "Good afternoon" before 5, then "Good evening"
  const now = new Date();
  let greeting = 'Good evening';
  if (now.getHours() < 12) {
    greeting = 'Good morning';
  } else if (now.getHours() < 17) {
    greeting = 'Good afternoon';
  }
  const todayText = now.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Title */}
      <header className="register-rule pb-5">
        <p className="text-sm text-gray-500">{todayText}</p>
        <h1 className="mt-1 text-3xl sm:text-[2.1rem] font-semibold text-gray-900">
          {greeting}, {user?.name || user?.username || 'there'}
        </h1>
      </header>

      {/* The figures, in one ruled row */}
      <section aria-label="Summary">
        <dl className={`grid grid-cols-2 ${statCards.length >= 4 ? 'lg:grid-cols-4' : statCards.length === 3 ? 'lg:grid-cols-3' : 'lg:grid-cols-2'} bg-white border border-gray-200 rounded-lg overflow-hidden`}>
          {statCards.map((card, index) => {
            const inner = (
              <>
                <dt className="text-sm text-gray-600">{card.title}</dt>
                <dd className="mt-1 font-serif text-[2rem] leading-none font-semibold text-gray-900 tabular">{card.value}</dd>
              </>
            );
            const borders = `${index % 2 === 1 ? 'border-l' : ''} ${index >= 2 ? 'border-t lg:border-t-0' : ''} ${index > 0 ? 'lg:border-l' : ''} border-gray-200`;
            if (card.path) {
              return (
                <button
                  key={card.title}
                  onClick={() => navigate(card.path!)}
                  className={`group text-left px-5 py-4 hover:bg-gray-50 transition-colors ${borders}`}
                >
                  {inner}
                  <span className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary-700 opacity-80 group-hover:opacity-100">
                    Open <ArrowRight size={12} />
                  </span>
                </button>
              );
            }
            return (
              <div key={card.title} className={`px-5 py-4 ${borders}`}>
                {inner}
              </div>
            );
          })}
        </dl>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Shortcuts */}
        <section className="lg:col-span-3">
          <h2 className="text-base font-semibold text-gray-900 mb-3">Shortcuts</h2>
          <ul className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-200">
            {shortcuts.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path}>
                  <button
                    onClick={() => navigate(item.path)}
                    className="group w-full flex items-center gap-4 px-5 py-3.5 text-left hover:bg-gray-50 transition-colors"
                  >
                    <Icon size={18} className="text-primary-600 shrink-0" />
                    <span className="flex-1 min-w-0">
                      <span className="block text-sm font-semibold text-gray-900">{item.label}</span>
                      <span className="block text-sm text-gray-500 truncate">{item.note}</span>
                    </span>
                    <ArrowRight size={16} className="text-gray-400 group-hover:text-primary-600 transition-colors" />
                  </button>
                </li>
              );
            })}
          </ul>
        </section>

        {/* Coming up */}
        <section className="lg:col-span-2 space-y-6">
          <div>
            <div className="flex items-baseline justify-between mb-3">
              <h2 className="text-base font-semibold text-gray-900">Coming up</h2>
              {/* Only the admin has an Events page to manage them */}
              {userRole === 'admin' && (
                <button onClick={() => navigate('/admin/events')} className="text-sm font-medium text-primary-700 hover:underline">
                  Manage events
                </button>
              )}
            </div>
            {stats.events > 0 ? (
              <ul className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-200">
                {upcomingEvents.slice(0, 5).map((event) => {
                  const date = new Date(event.event_date + 'T00:00:00');
                  return (
                    <li key={event.id} className="flex items-center gap-4 px-5 py-3">
                      <div className="w-11 shrink-0 text-center border-r border-gray-200 pr-4">
                        <p className="font-serif text-xl leading-none font-semibold text-gray-900 tabular">{date.getDate()}</p>
                        <p className="text-[11px] font-semibold uppercase tracking-wide text-brass-600 mt-1">
                          {date.toLocaleDateString('en-GB', { month: 'short' })}
                        </p>
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-gray-900">{event.title}</p>
                        <p className="text-sm text-gray-500">
                          {date.toLocaleDateString('en-GB', { weekday: 'long' })}
                          {event.event_time ? ` · ${event.event_time}` : ''}
                        </p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="bg-white border border-gray-200 rounded-lg px-5 py-6 text-sm text-gray-500">
                No events coming up.{userRole === 'admin' ? ' Holidays, meetings and school days you add will be listed here.' : ''}
              </p>
            )}
          </div>

          {stats.announcements > 0 && (
            <button
              onClick={() => navigate(`/${userRole}/announcements`)}
              className="group w-full flex items-center gap-4 bg-white border border-gray-200 rounded-lg px-5 py-3.5 text-left hover:bg-gray-50 transition-colors"
            >
              <Bell size={18} className="text-primary-600 shrink-0" />
              <span className="flex-1 text-sm">
                <span className="font-semibold text-gray-900 tabular">{stats.announcements}</span>{' '}
                <span className="text-gray-700">{stats.announcements === 1 ? 'announcement' : 'announcements'}</span>
              </span>
              <ArrowRight size={16} className="text-gray-400 group-hover:text-primary-600 transition-colors" />
            </button>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
