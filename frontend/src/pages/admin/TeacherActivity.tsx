import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, AlertTriangle, BookOpen, PenSquare, FileText, Clock } from 'lucide-react';
import { getTeacherActivity } from '../../services/api';
import type { TeacherActivity } from '../../types';
import { showError } from '../../utils/errorHandler';

// One teacher's work, for the admin: their classes and syllabus progress, what they
// did in the last 7 days, marks they still have to enter, and their recent actions.
const AdminTeacherActivity: React.FC = () => {
  const { teacherId } = useParams();
  const navigate = useNavigate();
  const [teacher, setTeacher] = useState<TeacherActivity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const data = await getTeacherActivity(Number(teacherId));
        setTeacher(data);
      } catch (error: any) {
        showError(error, "Failed to load the teacher's activity");
      } finally {
        setLoading(false);
      }
    };
    fetchActivity();
  }, [teacherId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!teacher) {
    return (
      <div className="space-y-4">
        <button onClick={() => navigate('/admin/oversight')} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1">
          <ArrowLeft size={16} /> Oversight
        </button>
        <div className="card text-gray-500">This teacher's activity can't be shown.</div>
      </div>
    );
  }

  const weekCards = [
    { label: 'Attendance days marked', value: teacher.this_week.attendance_days_marked },
    { label: 'Diary entries', value: teacher.this_week.diary_entries },
    { label: 'Assignments', value: teacher.this_week.assignments },
    { label: 'Class tests', value: teacher.this_week.class_tests },
    { label: 'Syllabus updates', value: teacher.this_week.progress_updates },
    { label: 'Actions', value: teacher.this_week.actions },
  ];

  const openFullLog = () => {
    // IDs are counted separately for admins, teachers and students, so the role is needed too
    navigate(`/admin/activity?role=teacher&user_id=${teacher.id}&name=${encodeURIComponent(teacher.name)}`);
  };

  return (
    <div className="print-area space-y-6">
      <div className="no-print flex items-center justify-between">
        <button onClick={() => navigate('/admin/oversight')} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1">
          <ArrowLeft size={16} /> Oversight
        </button>
        <button onClick={() => window.print()} className="btn btn-primary flex items-center gap-2">
          <Printer size={16} /> Print
        </button>
      </div>

      {/* Who */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{teacher.name}</h1>
        <p className="text-gray-600 mt-2">{teacher.username} · {teacher.email}</p>
        <div className="flex flex-wrap gap-6 mt-3 text-sm">
          <div><span className="text-gray-500">Last login: </span><span className="font-semibold">{teacher.last_login || 'Never'}</span></div>
          <div><span className="text-gray-500">Last active: </span><span className="font-semibold">{teacher.last_active || 'Never'}</span></div>
        </div>
      </div>

      {/* Last 7 days */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">Last 7 days</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {weekCards.map((item) => (
            <div key={item.label} className="card text-center">
              <div className="text-2xl font-bold text-gray-900">{item.value}</div>
              <div className="text-xs text-gray-500 mt-1">{item.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {teacher.attendance_not_marked_today.length > 0 && (
        <div className="card border-2 border-orange-300 bg-orange-50 flex items-center gap-2 text-orange-700">
          <AlertTriangle size={18} />
          Today's attendance not marked yet: {teacher.attendance_not_marked_today.join(', ')}
        </div>
      )}
      {teacher.marks_pending.length > 0 && (
        <div className="card border-2 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-700 font-semibold mb-2">
            <AlertTriangle size={18} /> Exam marks still to enter
          </div>
          <ul className="text-sm text-red-700 space-y-1">
            {teacher.marks_pending.map((item, index) => (
              <li key={index}>
                {item.term_name}: {item.subject_name} in {item.section_name} ({item.entered} of {item.student_count} entered)
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Classes */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Classes</h2>
        </div>
        <p className="text-sm mb-4">
          <span className="text-gray-500">Class incharge of: </span>
          <span className="font-semibold">{teacher.incharge_of.length > 0 ? teacher.incharge_of.join(', ') : 'none'}</span>
        </p>
        {teacher.teaching.length === 0 ? (
          <p className="text-sm text-gray-500">The admin hasn't given this teacher any subjects yet.</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="table text-sm">
                <thead>
                  <tr>
                    <th>Section</th>
                    <th>Subject</th>
                    <th>Syllabus Progress</th>
                    <th>Periods / Week</th>
                  </tr>
                </thead>
                <tbody>
                  {teacher.teaching.map((item) => (
                    <tr key={`${item.section_id}-${item.subject_name}`}>
                      <td>{item.section_name}</td>
                      <td>{item.subject_name}</td>
                      <td className="min-w-[12rem]">
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div className="h-2 bg-green-500 rounded-full" style={{ width: `${item.percentage}%` }}></div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {item.chapters_done} of {item.chapter_count} chapters ({item.percentage}%)
                        </div>
                      </td>
                      <td>{item.periods_per_week}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-sm text-gray-600 mt-3">Total periods per week: <span className="font-semibold">{teacher.periods_per_week}</span></p>
          </>
        )}
      </div>

      {/* Diary this week */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <PenSquare size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Diary This Week</h2>
        </div>
        {teacher.diary_this_week.length === 0 ? (
          <p className="text-sm text-gray-500">No diary entries in the last 7 days.</p>
        ) : (
          <div className="space-y-3">
            {teacher.diary_this_week.map((entry, index) => (
              <div key={index} className="border border-gray-200 rounded-xl p-3 text-sm">
                <div className="font-semibold text-gray-900">{entry.date} · {entry.subject_name} · {entry.section_name}</div>
                {entry.classwork && <div className="mt-1"><span className="text-gray-500">Classwork: </span>{entry.classwork}</div>}
                {entry.homework && <div className="mt-1"><span className="text-gray-500">Homework: </span>{entry.homework}</div>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Assignments this week */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <FileText size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Assignments This Week</h2>
        </div>
        {teacher.assignments_this_week.length === 0 ? (
          <p className="text-sm text-gray-500">No assignments set in the last 7 days.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table text-sm">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Subject</th>
                  <th>Section</th>
                  <th>Due</th>
                  <th>Set On</th>
                </tr>
              </thead>
              <tbody>
                {teacher.assignments_this_week.map((assignment, index) => (
                  <tr key={index}>
                    <td className="font-semibold">{assignment.title}</td>
                    <td>{assignment.subject_name}</td>
                    <td>{assignment.section_name || '-'}</td>
                    <td>{assignment.due_date}</td>
                    <td>{assignment.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent actions */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <div className="flex items-center gap-2">
            <Clock size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Recent Actions</h2>
          </div>
          <button onClick={openFullLog} className="no-print text-sm text-primary-600 hover:underline">See the full activity log</button>
        </div>
        {teacher.recent_actions.length === 0 ? (
          <p className="text-sm text-gray-500">No actions recorded yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table text-sm">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>What</th>
                  <th>Area</th>
                  <th>IP Address</th>
                </tr>
              </thead>
              <tbody>
                {teacher.recent_actions.map((entry) => (
                  <tr key={entry.id}>
                    <td className="whitespace-nowrap">{entry.created_at}</td>
                    <td>{entry.description}</td>
                    <td className="capitalize">{entry.area}</td>
                    <td>{entry.ip_address || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminTeacherActivity;
