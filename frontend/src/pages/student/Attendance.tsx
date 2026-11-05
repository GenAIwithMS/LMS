import React, { useState, useEffect } from 'react';
import { TrendingUp, CheckCircle, XCircle, Clock, CalendarOff } from 'lucide-react';
import { getMyDailyAttendance } from '../../services/api';
import type { MyDailyAttendance, AttendanceStatus } from '../../types';
import { showError } from '../../utils/errorHandler';

// The badge colour and label for each status.
const STATUS_BADGES: Record<AttendanceStatus, { label: string; badgeClass: string }> = {
  present: { label: 'Present', badgeClass: 'bg-green-100 text-green-800' },
  absent: { label: 'Absent', badgeClass: 'bg-red-100 text-red-800' },
  late: { label: 'Late', badgeClass: 'bg-yellow-100 text-yellow-800' },
  leave: { label: 'Leave', badgeClass: 'bg-blue-100 text-blue-800' },
};

// A student's own daily attendance, marked by their class incharge.
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// "2026-11-05" -> "5 Nov 2026" (the day first). Read from the text, so time zones can't move it.
const dateText = (value: string | null | undefined): string => {
  if (!value) {
    return '-';
  }
  const parts = value.slice(0, 10).split('-');
  if (parts.length !== 3) {
    return value;
  }
  const month = MONTHS[parseInt(parts[1], 10) - 1];
  const day = parseInt(parts[2], 10);
  if (!month || isNaN(day)) {
    return value;
  }
  return `${day} ${month} ${parts[0]}`;
};

const StudentAttendance: React.FC = () => {
  const [attendance, setAttendance] = useState<MyDailyAttendance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAttendance();
  }, []);

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      const data = await getMyDailyAttendance();
      setAttendance(data);
    } catch (error: any) {
      showError(error, 'Failed to load your attendance');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  let summary = { present: 0, absent: 0, late: 0, leave: 0, total_days: 0, percentage: null as number | null };
  let records: MyDailyAttendance['records'] = [];
  if (attendance) {
    summary = attendance.summary;
    records = attendance.records;
  }

  // Below 75% is shown in red
  let percentageClass = 'text-gray-900';
  if (summary.percentage !== null && summary.percentage < 75) {
    percentageClass = 'text-red-600';
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Attendance</h1>
        <p className="text-gray-600 mt-2">Your daily attendance, marked by your class incharge</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><TrendingUp size={16} /> Attendance</div>
          <div className={`text-2xl font-bold mt-1 ${percentageClass}`}>{summary.percentage === null ? '-' : `${summary.percentage}%`}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><CheckCircle size={16} className="text-green-600" /> Present</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{summary.present}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><XCircle size={16} className="text-red-600" /> Absent</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{summary.absent}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><Clock size={16} className="text-yellow-600" /> Late</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{summary.late}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 text-sm text-gray-500"><CalendarOff size={16} className="text-blue-600" /> Leave</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{summary.leave}</div>
        </div>
      </div>

      {/* Day by day */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Day by Day</h2>
        {records.length === 0 ? (
          <p className="text-sm text-gray-500">No attendance has been marked for you yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Marked By</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => {
                  const badge = STATUS_BADGES[record.status];
                  return (
                    <tr key={record.id}>
                      <td>{dateText(record.date)}</td>
                      <td>
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${badge ? badge.badgeClass : 'bg-gray-100 text-gray-800'}`}>
                          {badge ? badge.label : record.status}
                        </span>
                      </td>
                      <td>{record.marked_by || '-'}</td>
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

export default StudentAttendance;
