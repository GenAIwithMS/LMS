import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, UserCheck, BookOpen, Users, CalendarDays, ListChecks, PenSquare, ClipboardCheck, Plus } from 'lucide-react';
import { getClassSection, setSubjectTeacher, getTeachers, getSectionTimetable, getSectionAttendance, addClassSubject } from '../services/api';
import type { SectionDetails, Teacher, Timetable, AttendanceRegister } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { TimetableGrid } from '../components/TimetableGrid';
import { ProgressView } from '../components/ProgressView';
import { DiaryView } from '../components/DiaryView';
import { showError, showSuccess } from '../utils/errorHandler';
import { todayText } from '../utils/date';

type Tab = 'overview' | 'timetable' | 'progress' | 'diary' | 'attendance';

const STATUS_COLOURS: Record<string, string> = {
  present: 'bg-green-100 text-green-800',
  absent: 'bg-red-100 text-red-800',
  late: 'bg-yellow-100 text-yellow-800',
  leave: 'bg-blue-100 text-blue-800',
};

// One section (for example Class 5 - A), in tabs:
// - Overview: class incharge, who teaches each subject, and the students
// - Timetable: the weekly periods (the admin makes it on the Timetable page)
// - Syllabus progress: how far each subject has got (subject teachers update theirs)
// - Diary: classwork and homework by day (subject teachers write theirs)
// - Attendance: the day's register (the class incharge marks it on the Attendance page)
const SectionDetail: React.FC = () => {
  const { sectionId } = useParams();
  const navigate = useNavigate();
  const { userRole, user } = useAuth();
  const isAdmin = userRole === 'admin';

  const [section, setSection] = useState<SectionDetails | null>(null);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('overview');

  const [timetable, setTimetable] = useState<Timetable | null>(null);
  const [newSubjectName, setNewSubjectName] = useState('');

  const [attendanceDate, setAttendanceDate] = useState(todayText());
  const [register, setRegister] = useState<AttendanceRegister | null>(null);

  useEffect(() => {
    fetchSection();
    if (isAdmin) {
      fetchTeachers();
    }
  }, [sectionId]);

  useEffect(() => {
    if (tab === 'timetable') {
      fetchTimetable();
    }
    if (tab === 'attendance') {
      fetchRegister();
    }
  }, [tab, sectionId, attendanceDate]);

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchSection = async () => {
    try {
      const data = await getClassSection(Number(sectionId));
      setSection(data);
    } catch (error: any) {
      showError(error, 'Failed to load the section');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeachers = async () => {
    try {
      const data = await getTeachers();
      setTeachers(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load teachers');
    }
  };

  const fetchTimetable = async () => {
    try {
      const data = await getSectionTimetable(Number(sectionId));
      setTimetable(data);
    } catch (error: any) {
      showError(error, 'Failed to load the timetable');
    }
  };

  const fetchRegister = async () => {
    try {
      const data = await getSectionAttendance(Number(sectionId), attendanceDate);
      setRegister(data);
    } catch (error: any) {
      showError(error, 'Failed to load the attendance');
    }
  };

  const handleTeacherChange = async (subjectId: number, teacherId: string) => {
    try {
      const data = await setSubjectTeacher(Number(sectionId), subjectId, teacherId ? Number(teacherId) : null);
      showSuccess(data.message || 'Subject teacher updated');
      fetchSection();
    } catch (error: any) {
      // For example: the new teacher is busy in another section in one of this subject's periods
      showError(error, 'Failed to change the subject teacher');
    }
  };

  // The admin can add a subject to this section's class straight from here
  const handleAddSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!section || !section.class_id || !newSubjectName.trim()) return;
    try {
      await addClassSubject(section.class_id, newSubjectName.trim());
      showSuccess(`${newSubjectName.trim()} added to ${section.class_name || 'the class'}`);
      setNewSubjectName('');
      fetchSection();
    } catch (error: any) {
      showError(error, 'Failed to add the subject');
    }
  };

  if (loading || !section) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  let backPath = '/teacher/classes';
  let backLabel = 'My classes';
  if (isAdmin) {
    backPath = section.class_id ? `/admin/classes/${section.class_id}` : '/admin/classes';
    backLabel = section.class_name || 'Classes';
  }

  // The subjects the logged-in teacher teaches in this section
  const mySubjects: { subject_id: number; subject_name: string }[] = [];
  if (userRole === 'teacher' && user) {
    for (const item of section.subjects) {
      if (item.teacher_id === user.id) {
        mySubjects.push({ subject_id: item.subject_id, subject_name: item.subject_name });
      }
    }
  }
  const mySubjectIds = mySubjects.map((subject) => subject.subject_id);
  const isIncharge = userRole === 'teacher' && user !== null && section.incharge_id === user.id;

  // The admin's form to add a subject to the class (every section of the class gets it)
  const addSubjectForm = (
    <form onSubmit={handleAddSubject} className="flex gap-2 mt-4">
      <input type="text" placeholder="New subject, e.g. Maths" value={newSubjectName} onChange={(e) => setNewSubjectName(e.target.value)} className="input max-w-xs" />
      <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Add Subject</button>
    </form>
  );

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'overview', label: 'Overview', icon: <Users size={16} /> },
    { key: 'timetable', label: 'Timetable', icon: <CalendarDays size={16} /> },
    { key: 'progress', label: 'Syllabus Progress', icon: <ListChecks size={16} /> },
    { key: 'diary', label: 'Diary', icon: <PenSquare size={16} /> },
    { key: 'attendance', label: 'Attendance', icon: <ClipboardCheck size={16} /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <button onClick={() => navigate(backPath)} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1 mb-2">
          <ArrowLeft size={16} /> {backLabel}
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{section.full_name}</h1>
        <p className="text-gray-600 mt-2 flex items-center gap-2">
          <UserCheck size={16} /> Class incharge: <span className="font-semibold">{section.incharge_name || 'not chosen yet'}</span>
        </p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-gray-200">
        {tabs.map((item) => (
          <button
            key={item.key}
            onClick={() => setTab(item.key)}
            className={`px-4 py-2 text-sm font-medium flex items-center gap-2 border-b-2 -mb-px ${tab === item.key ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}
          >
            {item.icon} {item.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        <>
          {/* Subject teachers */}
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen size={20} className="text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Subject Teachers</h2>
            </div>
            {section.subjects.length === 0 ? (
              isAdmin ? (
                <div>
                  <p className="text-sm text-gray-500">This class has no subjects yet. Add the subjects it studies, e.g. English, Urdu, Maths.</p>
                  {addSubjectForm}
                </div>
              ) : (
                <p className="text-sm text-gray-500">This class has no subjects yet. The admin adds them.</p>
              )
            ) : (
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Teacher</th>
                    </tr>
                  </thead>
                  <tbody>
                    {section.subjects.map((item) => (
                      <tr key={item.subject_id}>
                        <td className="font-semibold">{item.subject_name}</td>
                        <td>
                          {isAdmin ? (
                            <select value={item.teacher_id ? String(item.teacher_id) : ''} onChange={(e) => handleTeacherChange(item.subject_id, e.target.value)} className="input py-1">
                              <option value="">No teacher yet</option>
                              {teachers.map((teacher) => (
                                <option key={teacher.id} value={teacher.id}>{teacher.name} ({teacher.username})</option>
                              ))}
                            </select>
                          ) : (
                            <span>{item.teacher_name || <span className="text-gray-400">No teacher yet</span>}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {isAdmin && (
                  <div>
                    <p className="text-sm text-gray-500 mt-4">Add another subject to the class:</p>
                    {addSubjectForm}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Students */}
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <Users size={20} className="text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Students ({section.students.length})</h2>
            </div>
            {section.students.length === 0 ? (
              <p className="text-sm text-gray-500">No students in this section yet. The admin adds them on the Students page.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Roll No.</th>
                      <th>Name</th>
                      <th>Username</th>
                    </tr>
                  </thead>
                  <tbody>
                    {section.students.map((student) => (
                      <tr key={student.id}>
                        <td>{student.roll_number || '-'}</td>
                        <td>{student.name}</td>
                        <td>{student.username}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {tab === 'timetable' && (
        <div className="card">
          <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Weekly Timetable</h2>
              <p className="text-sm text-gray-500">
                {isAdmin
                  ? 'This is the draft. Changes are seen by teachers and students after you publish.'
                  : 'Every day of the week, with the teacher of each period.'}
              </p>
            </div>
            {isAdmin && (
              <button onClick={() => navigate(`/admin/timetable?section=${section.id}`)} className="btn btn-primary flex items-center gap-1">
                <CalendarDays size={16} /> Edit in Timetable builder
              </button>
            )}
          </div>
          {!timetable ? (
            <p className="text-sm text-gray-400">Loading the timetable...</p>
          ) : !isAdmin && timetable.is_published === false ? (
            <p className="text-sm text-gray-500">The timetable hasn't been published yet.</p>
          ) : (
            <TimetableGrid timetable={timetable} />
          )}
        </div>
      )}

      {tab === 'progress' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Syllabus Progress</h2>
          <p className="text-sm text-gray-500 mb-4">
            {mySubjects.length > 0
              ? 'Open your subject to mark each chapter as in progress or done.'
              : 'How much of each subject this section has covered.'}
          </p>
          <ProgressView sectionId={section.id} editableSubjectIds={mySubjectIds} />
        </div>
      )}

      {tab === 'diary' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Daily Diary</h2>
          <DiaryView sectionId={section.id} writableSubjects={mySubjects} />
        </div>
      )}

      {tab === 'attendance' && (
        <div className="card">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Attendance</h2>
            <div className="flex items-center gap-2">
              <input type="date" value={attendanceDate} max={todayText()} onChange={(e) => setAttendanceDate(e.target.value)} className="input max-w-[12rem]" />
              {isIncharge && (
                <button onClick={() => navigate('/teacher/attendance')} className="btn btn-primary text-sm">Mark attendance</button>
              )}
            </div>
          </div>
          {!register ? (
            <p className="text-sm text-gray-400">Loading the attendance...</p>
          ) : register.students.length === 0 ? (
            <p className="text-sm text-gray-500">No students in this section yet.</p>
          ) : (
            <>
              <p className="text-sm mb-3">
                {register.is_marked
                  ? <span className="text-green-700">Marked for this day.</span>
                  : <span className="text-orange-600">Not marked yet ({register.marked_count} of {register.students.length} students). The class incharge marks it.</span>}
              </p>
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Roll No.</th>
                      <th>Name</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {register.students.map((student) => (
                      <tr key={student.student_id}>
                        <td>{student.roll_number || '-'}</td>
                        <td>{student.name}</td>
                        <td>
                          {student.status ? (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${STATUS_COLOURS[student.status]}`}>{student.status}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default SectionDetail;
