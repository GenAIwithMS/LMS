import React, { useState, useEffect } from 'react';
import { CalendarCheck, CheckCircle, Save, BarChart3, UserCheck } from 'lucide-react';
import { getMyClasses, getSectionAttendance, saveSectionAttendance, getSectionAttendanceSummary } from '../../services/api';
import type { ClassSection, AttendanceRegister, AttendanceStatus, StudentMonthSummary } from '../../types';
import toast from 'react-hot-toast';
import { showError, showSuccess } from '../../utils/errorHandler';

// The four choices for each student, with the colour of the selected button.
const STATUS_OPTIONS: { value: AttendanceStatus; label: string; selectedClass: string }[] = [
  { value: 'present', label: 'Present', selectedClass: 'bg-green-600 text-white border-green-600' },
  { value: 'absent', label: 'Absent', selectedClass: 'bg-red-600 text-white border-red-600' },
  { value: 'late', label: 'Late', selectedClass: 'bg-yellow-500 text-white border-yellow-500' },
  { value: 'leave', label: 'Leave', selectedClass: 'bg-blue-600 text-white border-blue-600' },
];

// Today as "2026-11-04", in the user's own time zone.
const todayText = () => {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
};

// Daily attendance: the class incharge marks every student of their section
// once a day, and can see a monthly summary.
const TeacherAttendance: React.FC = () => {
  const [inchargeSections, setInchargeSections] = useState<ClassSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [sectionId, setSectionId] = useState<number | null>(null);
  const [date, setDate] = useState(todayText());

  const [register, setRegister] = useState<AttendanceRegister | null>(null);
  const [statuses, setStatuses] = useState<Record<number, AttendanceStatus | null>>({});
  const [saving, setSaving] = useState(false);

  const [month, setMonth] = useState(todayText().slice(0, 7));
  const [summary, setSummary] = useState<StudentMonthSummary[]>([]);

  useEffect(() => {
    fetchMySections();
  }, []);

  useEffect(() => {
    if (sectionId) {
      fetchRegister();
    }
  }, [sectionId, date]);

  useEffect(() => {
    if (sectionId) {
      fetchSummary();
    }
  }, [sectionId, month]);

  const fetchMySections = async () => {
    try {
      setLoading(true);
      const data = await getMyClasses();
      const sections = Array.isArray(data.incharge_of) ? data.incharge_of : [];
      setInchargeSections(sections);
      if (sections.length > 0) {
        setSectionId(sections[0].id);
      }
    } catch (error: any) {
      showError(error, 'Failed to load your sections');
    } finally {
      setLoading(false);
    }
  };

  const fetchRegister = async () => {
    if (!sectionId) return;
    try {
      const data = await getSectionAttendance(sectionId, date);
      setRegister(data);
      // Start from what is already saved for this day
      const saved: Record<number, AttendanceStatus | null> = {};
      for (const student of data.students) {
        saved[student.student_id] = student.status;
      }
      setStatuses(saved);
    } catch (error: any) {
      showError(error, 'Failed to load the attendance register');
    }
  };

  const fetchSummary = async () => {
    if (!sectionId) return;
    try {
      const data = await getSectionAttendanceSummary(sectionId, month);
      setSummary(Array.isArray(data.students) ? data.students : []);
    } catch (error: any) {
      showError(error, 'Failed to load the monthly summary');
    }
  };

  const setStudentStatus = (studentId: number, status: AttendanceStatus) => {
    setStatuses({ ...statuses, [studentId]: status });
  };

  const markAllPresent = () => {
    if (!register) return;
    const allPresent: Record<number, AttendanceStatus | null> = {};
    for (const student of register.students) {
      allPresent[student.student_id] = 'present';
    }
    setStatuses(allPresent);
  };

  const handleSave = async () => {
    if (!register || !sectionId) return;

    // Every student must get a status before saving
    const records: { student_id: number; status: string }[] = [];
    let missingCount = 0;
    for (const student of register.students) {
      const status = statuses[student.student_id];
      if (status) {
        records.push({ student_id: student.student_id, status: status });
      } else {
        missingCount = missingCount + 1;
      }
    }
    if (missingCount > 0) {
      if (missingCount === 1) {
        toast.error('1 student has no status yet. Choose one for every student.');
      } else {
        toast.error(`${missingCount} students have no status yet. Choose one for every student.`);
      }
      return;
    }

    try {
      setSaving(true);
      const data = await saveSectionAttendance(sectionId, date, records);
      showSuccess(data.message || 'Attendance saved');
      fetchRegister();
      fetchSummary();
    } catch (error: any) {
      showError(error, 'Failed to save the attendance');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (inchargeSections.length === 0) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Attendance</h1>
          <p className="text-gray-600 mt-2">Daily attendance for your section</p>
        </div>
        <div className="card flex items-center gap-3">
          <UserCheck size={24} className="text-gray-400" />
          <p className="text-gray-600">Only the class incharge marks attendance. You are not the class incharge of any section.</p>
        </div>
      </div>
    );
  }

  // Counts for the day, from the choices on screen
  const counts = { present: 0, absent: 0, late: 0, leave: 0 };
  if (register) {
    for (const student of register.students) {
      const status = statuses[student.student_id];
      if (status) {
        counts[status] = counts[status] + 1;
      }
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Attendance</h1>
        <p className="text-gray-600 mt-2">Mark your section's attendance once a day</p>
      </div>

      {/* Daily register */}
      <div className="card">
        <div className="flex flex-wrap items-end justify-between gap-4 mb-4">
          <div className="flex items-center gap-2">
            <CalendarCheck size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Daily Register</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            {inchargeSections.length > 1 && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Section</label>
                <select value={sectionId ? String(sectionId) : ''} onChange={(e) => setSectionId(Number(e.target.value))} className="input">
                  {inchargeSections.map((section) => (
                    <option key={section.id} value={section.id}>{section.full_name}</option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm text-gray-600 mb-1">Date</label>
              <input type="date" value={date} max={todayText()} onChange={(e) => setDate(e.target.value)} className="input" />
            </div>
          </div>
        </div>

        {register && (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <div className="text-sm text-gray-600">
                <span className="font-semibold text-gray-900">{register.section_name}</span>
                {' · '}
                {register.is_marked ? (
                  <span className="text-green-700 font-medium">Saved for this day</span>
                ) : (
                  <span className="text-orange-600 font-medium">Not marked yet</span>
                )}
              </div>
              <div className="text-sm text-gray-600">
                Present {counts.present} · Absent {counts.absent} · Late {counts.late} · Leave {counts.leave}
              </div>
            </div>

            {register.students.length === 0 ? (
              <p className="text-sm text-gray-500">This section has no students yet.</p>
            ) : (
              <>
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
                          <td className="font-semibold">{student.name}</td>
                          <td>
                            <div className="flex flex-wrap gap-1">
                              {STATUS_OPTIONS.map((option) => {
                                const isSelected = statuses[student.student_id] === option.value;
                                let buttonClass = 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50';
                                if (isSelected) {
                                  buttonClass = option.selectedClass;
                                }
                                return (
                                  <button
                                    key={option.value}
                                    type="button"
                                    onClick={() => setStudentStatus(student.student_id, option.value)}
                                    className={`px-3 py-1 text-sm rounded-lg border ${buttonClass}`}
                                  >
                                    {option.label}
                                  </button>
                                );
                              })}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex flex-wrap gap-2 mt-4">
                  <button type="button" onClick={markAllPresent} className="btn btn-secondary flex items-center gap-1">
                    <CheckCircle size={16} /> Mark all present
                  </button>
                  <button type="button" onClick={handleSave} disabled={saving} className="btn btn-primary flex items-center gap-1">
                    <Save size={16} /> {saving ? 'Saving...' : 'Save Attendance'}
                  </button>
                </div>
              </>
            )}
          </>
        )}
      </div>

      {/* Monthly summary */}
      <div className="card">
        <div className="flex flex-wrap items-end justify-between gap-4 mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Monthly Summary</h2>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Month</label>
            <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} className="input" />
          </div>
        </div>
        {summary.length === 0 ? (
          <p className="text-sm text-gray-500">No students in this section yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Roll No.</th>
                  <th>Name</th>
                  <th>Present</th>
                  <th>Absent</th>
                  <th>Late</th>
                  <th>Leave</th>
                  <th>Percentage</th>
                </tr>
              </thead>
              <tbody>
                {summary.map((row) => {
                  // Below 75% is shown in red
                  let percentageClass = 'text-gray-900';
                  if (row.percentage !== null && row.percentage < 75) {
                    percentageClass = 'text-red-600 font-semibold';
                  }
                  return (
                    <tr key={row.student_id}>
                      <td>{row.roll_number || '-'}</td>
                      <td className="font-semibold">{row.name}</td>
                      <td>{row.present}</td>
                      <td>{row.absent}</td>
                      <td>{row.late}</td>
                      <td>{row.leave}</td>
                      <td className={percentageClass}>{row.percentage === null ? '-' : `${row.percentage}%`}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherAttendance;
