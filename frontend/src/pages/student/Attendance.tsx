import React, { useState, useEffect } from 'react';
import { Search, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react';
import { getAttendance } from '../../services/api';
import type { Attendance } from '../../types';
import toast from 'react-hot-toast';

const StudentAttendance: React.FC = () => {
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAttendance();
  }, []);

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      console.log('Fetching attendance...');
      const data = await getAttendance();
      console.log('Attendance API response:', data);
      
      // Handle different response formats
      let attendanceData: Attendance[] = [];
      
      if (Array.isArray(data)) {
        attendanceData = data;
      } else if (data && Array.isArray(data.attendance)) {
        attendanceData = data.attendance;
      } else if (data && data.attendance_record) {
        attendanceData = Array.isArray(data.attendance_record) ? data.attendance_record : [data.attendance_record];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const attendanceArray = Object.values(data).find((val) => Array.isArray(val)) as Attendance[] | undefined;
        if (attendanceArray) {
          attendanceData = attendanceArray;
        }
      }
      
      // Ensure all attendance records have required fields with defaults
      attendanceData = attendanceData.map((record: any) => ({
        id: record.id || 0,
        student: record.student || record.student_name || '',
        subject: record.subject || record.subject_name || '',
        status: (record.status || 'present') as 'present' | 'absent' | 'late',
        mark_at: record.mark_at || record.markAt || record.date || new Date().toISOString(),
      }));
      
      console.log('Processed attendance:', attendanceData);
      setAttendance(attendanceData);
    } catch (error: any) {
      console.error('Error fetching attendance:', error);
      toast.error(error.response?.data?.message || 'Failed to fetch attendance');
      setAttendance([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredAttendance = attendance.filter((record) => {
    const subject = record?.subject || '';
    const search = searchTerm.toLowerCase();
    return subject.toLowerCase().includes(search);
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'absent':
        return <XCircle className="text-red-600" size={20} />;
      case 'late':
        return <Clock className="text-yellow-600" size={20} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present':
        return 'bg-green-100 text-green-800';
      case 'absent':
        return 'bg-red-100 text-red-800';
      case 'late':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const attendanceStats = {
    present: attendance.filter((a) => a.status === 'present').length,
    absent: attendance.filter((a) => a.status === 'absent').length,
    late: attendance.filter((a) => a.status === 'late').length,
    total: attendance.length,
  };

  const attendancePercentage =
    attendanceStats.total > 0
      ? ((attendanceStats.present / attendanceStats.total) * 100).toFixed(1)
      : '0';

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">My Attendance</h1>
        <p className="text-gray-600 mt-2">View your attendance records</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">{attendanceStats.total}</p>
            </div>
            <div className="p-3 bg-gray-100 rounded-lg">
              <Clock className="text-gray-600" size={24} />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Present</p>
              <p className="text-2xl font-bold text-green-600">{attendanceStats.present}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="text-green-600" size={24} />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Absent</p>
              <p className="text-2xl font-bold text-red-600">{attendanceStats.absent}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <XCircle className="text-red-600" size={24} />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Attendance %</p>
              <p className="text-2xl font-bold text-primary-600">{attendancePercentage}%</p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <TrendingUp className="text-primary-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search attendance..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Subject</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredAttendance.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-8 text-gray-500">
                  No attendance records found
                </td>
              </tr>
            ) : (
              filteredAttendance.map((record) => (
                <tr key={record.id || Math.random()}>
                  <td>{record.id || 'N/A'}</td>
                  <td>{record.subject || 'N/A'}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(record.status || 'present')}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status || 'present')}`}>
                        {record.status || 'N/A'}
                      </span>
                    </div>
                  </td>
                  <td>{record.mark_at ? new Date(record.mark_at).toLocaleDateString() : 'N/A'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StudentAttendance;

