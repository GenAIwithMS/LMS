import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClipboardCheck, Users, GraduationCap, FileText, Printer, Download, ChevronDown, ChevronUp, AlertTriangle, ListChecks, Activity } from 'lucide-react';
import { getOversightDashboard, getTeachersOverview, downloadReport } from '../../services/api';
import type { OversightDashboard, TeachersOverview, SectionAttendanceToday } from '../../types';
import { showError } from '../../utils/errorHandler';

// The admin's oversight dashboard: what needs attention today.
// - which sections haven't marked attendance yet
// - what each teacher did in the last 7 days
// - exam marks still to be entered
// - how much of the syllabus each class has covered
// - students who are often absent
const AdminOversight: React.FC = () => {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<OversightDashboard | null>(null);
  const [teachers, setTeachers] = useState<TeachersOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [openClassId, setOpenClassId] = useState<number | null>(null);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const dashboardData = await getOversightDashboard();
        setDashboard(dashboardData);
        const teacherData = await getTeachersOverview();
        setTeachers(teacherData);
      } catch (error: any) {
        showError(error, 'Failed to load the oversight dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const handleDownload = async (name: string) => {
    try {
      await downloadReport(name);
    } catch (error: any) {
      showError(error, 'Failed to download the report');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!dashboard) {
    return <div className="card text-gray-500">The oversight dashboard can't be shown.</div>;
  }

  // Sections that haven't marked attendance come first
  const attendanceRows: SectionAttendanceToday[] = [];
  for (const row of dashboard.attendance_today) {
    if (!row.is_marked) {
      attendanceRows.push(row);
    }
  }
  for (const row of dashboard.attendance_today) {
    if (row.is_marked) {
      attendanceRows.push(row);
    }
  }

  const allMarked = dashboard.counts.sections_marked_today === dashboard.counts.sections;

  return (
    <div className="print-area space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Oversight</h1>
          <p className="text-gray-600 mt-2">What needs attention today, {dashboard.today}</p>
        </div>
        <div className="no-print flex gap-2">
          <button onClick={() => navigate('/admin/activity')} className="btn btn-secondary flex items-center gap-2">
            <Activity size={16} /> Activity Log
          </button>
          <button onClick={() => window.print()} className="btn btn-primary flex items-center gap-2">
            <Printer size={16} /> Print
          </button>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className={`card ${allMarked ? '' : 'border-2 border-orange-300 bg-orange-50'}`}>
          <div className="flex items-center gap-2 text-sm text-gray-500"><ClipboardCheck size={16} /> Sections marked today</div>
          <div className={`text-2xl font-bold mt-1 ${allMarked ? 'text-gray-900' : 'text-orange-600'}`}>
            {dashboard.counts.sections_marked_today} / {dashboard.counts.sections}
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><Users size={16} /> Students</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{dashboard.counts.students}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><GraduationCap size={16} /> Teachers</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{dashboard.counts.teachers}</div>
        </div>
        <button onClick={() => navigate('/admin/exams')} className="card text-left hover:shadow-md transition-all">
          <div className="flex items-center gap-2 text-sm text-gray-500"><FileText size={16} /> Question papers waiting</div>
          <div className={`text-2xl font-bold mt-1 ${dashboard.counts.question_papers_waiting > 0 ? 'text-orange-600' : 'text-gray-900'}`}>
            {dashboard.counts.question_papers_waiting}
          </div>
        </button>
      </div>

      {/* Today's attendance */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Today's Attendance</h2>
        {attendanceRows.length === 0 ? (
          <p className="text-sm text-gray-500">No sections yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table text-sm">
              <thead>
                <tr>
                  <th>Section</th>
                  <th>Class Incharge</th>
                  <th>Marked</th>
                  <th>Present</th>
                  <th>Absent</th>
                  <th>Late</th>
                  <th>Leave</th>
                </tr>
              </thead>
              <tbody>
                {attendanceRows.map((row) => (
                  <tr key={row.section_id} className={row.is_marked ? '' : 'bg-orange-50'}>
                    <td className="font-semibold">
                      {row.section_name}
                      {!row.is_marked && (
                        <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">Not marked</span>
                      )}
                    </td>
                    <td>{row.incharge_name || <span className="text-gray-400">No incharge</span>}</td>
                    <td>{row.marked_count} / {row.student_count}</td>
                    <td>{row.present}</td>
                    <td className={row.absent > 0 ? 'text-red-600' : ''}>{row.absent}</td>
                    <td>{row.late}</td>
                    <td>{row.leave}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Teachers this week */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
          <h2 className="text-lg font-semibold text-gray-900">Teachers This Week</h2>
          <button onClick={() => handleDownload('teachers')} className="no-print btn btn-secondary text-sm flex items-center gap-1">
            <Download size={14} /> Excel
          </button>
        </div>
        {teachers && (
          <p className="text-sm text-gray-500 mb-4">Last 7 days ({teachers.week_start} to {teachers.today})</p>
        )}
        {!teachers || teachers.teachers.length === 0 ? (
          <p className="text-sm text-gray-500">No teachers yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table text-sm">
              <thead>
                <tr>
                  <th>Teacher</th>
                  <th>Last Login</th>
                  <th>Attendance Days</th>
                  <th>Diary</th>
                  <th>Assignments</th>
                  <th>Class Tests</th>
                  <th>Syllabus Updates</th>
                  <th>Papers Missing Marks</th>
                  <th>Not Marked Today</th>
                </tr>
              </thead>
              <tbody>
                {teachers.teachers.map((teacher) => (
                  <tr key={teacher.id}>
                    <td>
                      <button onClick={() => navigate(`/admin/teachers/${teacher.id}/activity`)} className="text-primary-600 hover:underline font-medium text-left">
                        {teacher.name}
                      </button>
                    </td>
                    <td>{teacher.last_login || <span className="text-gray-400">Never</span>}</td>
                    <td>{teacher.this_week.attendance_days_marked}</td>
                    <td>{teacher.this_week.diary_entries}</td>
                    <td>{teacher.this_week.assignments}</td>
                    <td>{teacher.this_week.class_tests}</td>
                    <td>{teacher.this_week.progress_updates}</td>
                    <td className={teacher.papers_pending > 0 ? 'text-red-600 font-semibold' : ''}>{teacher.papers_pending}</td>
                    <td>
                      {teacher.attendance_not_marked_today.length > 0 ? (
                        <span className="text-orange-600 font-medium">{teacher.attendance_not_marked_today.join(', ')}</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Marks still to enter */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle size={20} className="text-red-500" />
          <h2 className="text-lg font-semibold text-gray-900">Marks Still To Enter</h2>
        </div>
        {dashboard.marks_pending.length === 0 ? (
          <p className="text-sm text-gray-500">All marks are in.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table text-sm">
              <thead>
                <tr>
                  <th>Exam</th>
                  <th>Section</th>
                  <th>Subject</th>
                  <th>Teacher</th>
                  <th>Entered</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.marks_pending.map((row, index) => (
                  <tr key={index}>
                    <td>{row.term_name}</td>
                    <td>{row.section_name}</td>
                    <td>{row.subject_name}</td>
                    <td>{row.teacher_name || <span className="text-gray-400">No teacher yet</span>}</td>
                    <td className="text-red-600 font-semibold">{row.entered} / {row.student_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Syllabus coverage */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <div className="flex items-center gap-2">
            <ListChecks size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Syllabus Coverage</h2>
          </div>
          <button onClick={() => handleDownload('syllabus')} className="no-print btn btn-secondary text-sm flex items-center gap-1">
            <Download size={14} /> Excel
          </button>
        </div>
        {dashboard.syllabus_coverage.length === 0 ? (
          <p className="text-sm text-gray-500">No classes with sections and subjects yet.</p>
        ) : (
          <div className="space-y-3">
            {dashboard.syllabus_coverage.map((schoolClass) => {
              const isOpen = openClassId === schoolClass.class_id;
              return (
                <div key={schoolClass.class_id} className="border border-gray-200 rounded-xl p-4">
                  <button onClick={() => setOpenClassId(isOpen ? null : schoolClass.class_id)} className="w-full text-left flex items-center justify-between">
                    <span className="font-semibold text-gray-900">{schoolClass.class_name}</span>
                    <span className="flex items-center gap-2 text-sm text-gray-600">
                      Average {schoolClass.average_percentage !== null ? `${schoolClass.average_percentage}%` : '-'}
                      {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </span>
                  </button>

                  <div className="mt-3 space-y-3">
                    {schoolClass.sections.map((section) => {
                      const percentage = section.average_percentage !== null ? section.average_percentage : 0;
                      return (
                        <div key={section.section_id}>
                          <div className="flex items-center justify-between text-sm">
                            <span>{section.section_name}</span>
                            <span className="text-gray-600">{section.average_percentage !== null ? `${section.average_percentage}%` : 'No chapters yet'}</span>
                          </div>
                          <div className="mt-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div className="h-2 bg-green-500 rounded-full" style={{ width: `${percentage}%` }}></div>
                          </div>

                          {isOpen && section.subjects.length > 0 && (
                            <div className="overflow-x-auto mt-2">
                              <table className="table text-sm">
                                <thead>
                                  <tr>
                                    <th>Subject</th>
                                    <th>Teacher</th>
                                    <th>Chapters Done</th>
                                    <th>Covered</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {section.subjects.map((subject) => (
                                    <tr key={subject.subject_name}>
                                      <td>{subject.subject_name}</td>
                                      <td>{subject.teacher_name || <span className="text-gray-400">No teacher yet</span>}</td>
                                      <td>{subject.chapters_done} / {subject.chapter_count}</td>
                                      <td>{subject.percentage}%</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Low attendance */}
      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Low Attendance (below {dashboard.low_attendance_percent}%)</h2>
          <button onClick={() => handleDownload('low-attendance')} className="no-print btn btn-secondary text-sm flex items-center gap-1">
            <Download size={14} /> Excel
          </button>
        </div>
        {dashboard.low_attendance.length === 0 ? (
          <p className="text-sm text-gray-500">No students below {dashboard.low_attendance_percent}% this session.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table text-sm">
              <thead>
                <tr>
                  <th>Section</th>
                  <th>Roll No.</th>
                  <th>Name</th>
                  <th>Attendance</th>
                  <th>Days Absent</th>
                  <th>Days Counted</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.low_attendance.map((student) => (
                  <tr key={student.student_id}>
                    <td>{student.section_name || '-'}</td>
                    <td>{student.roll_number || '-'}</td>
                    <td>{student.name}</td>
                    <td className="text-red-600 font-semibold">{student.percentage}%</td>
                    <td>{student.absent}</td>
                    <td>{student.days_counted}</td>
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

export default AdminOversight;
