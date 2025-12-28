import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getAttendance, markAttendance, updateAttendance, deleteAttendance, getStudents, getSubjects } from '../../services/api';
import type { Attendance, Student, Subject } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

const TeacherAttendance: React.FC = () => {
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState<Attendance | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingAttendance, setDeletingAttendance] = useState<Attendance | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterSubject, setFilterSubject] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const optionsRef = useRef<HTMLDivElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    student_name: '',
    subject_name: '',
    status: 'present' as 'present' | 'absent' | 'late',
  });

  useEffect(() => {
    fetchAttendance();
    fetchStudents();
    fetchSubjects();
  }, []);

  // Close options dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (optionsRef.current && !optionsRef.current.contains(event.target as Node)) {
        setShowOptions(false);
      }
    };

    if (showOptions) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showOptions]);

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
      showError(error, 'Failed to fetch attendance');
      setAttendance([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const data = await getStudents();
      setStudents(Array.isArray(data) ? data : data.student ? [data.student] : []);
    } catch (error) {
      console.error('Failed to fetch students');
    }
  };

  const fetchSubjects = async () => {
    try {
      const data = await getSubjects();
      console.log('Subjects API raw response:', data);
      
      // Handle different response formats
      let subjectsData: Subject[] = [];
      
      if (Array.isArray(data)) {
        subjectsData = data;
      } else if (data && Array.isArray(data.subjects)) {
        subjectsData = data.subjects;
      } else if (data && data.subject) {
        subjectsData = Array.isArray(data.subject) ? data.subject : [data.subject];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const subjectsArray = Object.values(data).find((val) => Array.isArray(val)) as Subject[] | undefined;
        if (subjectsArray) {
          subjectsData = subjectsArray;
        }
      }
      
      // Ensure all subjects have required fields
      subjectsData = subjectsData.map((subject: any) => ({
        id: subject.id || 0,
        name: subject.name || '',
        teacher: subject.teacher || subject.teacher_name || '',
        course: subject.course || subject.course_name || '',
      }));
      
      console.log('Processed subjects:', subjectsData);
      setSubjects(subjectsData);
    } catch (error: any) {
      console.error('Error fetching subjects:', error);
      showError(error, 'Failed to fetch subjects');
      setSubjects([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAttendance) {
        await updateAttendance(editingAttendance.id, formData);
        showSuccess('Attendance updated successfully');
      } else {
        await markAttendance(formData);
        showSuccess('Attendance marked successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchAttendance();
    } catch (error: any) {
      showError(error, 'Failed to save attendance');
    }
  };

  const handleEdit = (attendance: Attendance) => {
    setEditingAttendance(attendance);
    setFormData({
      student_name: attendance.student || '',
      subject_name: attendance.subject || '',
      status: attendance.status || 'present',
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (record: Attendance) => {
    setDeletingAttendance(record);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingAttendance) return;
    
    setIsDeleting(true);
    try {
      await deleteAttendance(deletingAttendance.id);
      showSuccess('Attendance deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingAttendance(null);
      fetchAttendance();
    } catch (error: any) {
      showError(error, 'Failed to delete attendance');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ student_name: '', subject_name: '', status: 'present' });
    setEditingAttendance(null);
  };

  const filteredAttendance = attendance
    .filter((record) => {
      const student = record?.student || '';
      const subject = record?.subject || '';
      const search = searchTerm.toLowerCase();
      const matchesSearch = student.toLowerCase().includes(search) || subject.toLowerCase().includes(search);
      const matchesSubject = filterSubject === 'all' || record.subject === filterSubject;
      const matchesStatus = filterStatus === 'all' || record.status === filterStatus;
      return matchesSearch && matchesSubject && matchesStatus;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'student':
          aValue = (a.student || '').toLowerCase();
          bValue = (b.student || '').toLowerCase();
          break;
        case 'subject':
          aValue = (a.subject || '').toLowerCase();
          bValue = (b.subject || '').toLowerCase();
          break;
        case 'status':
          aValue = (a.status || '').toLowerCase();
          bValue = (b.status || '').toLowerCase();
          break;
        case 'mark_at':
          aValue = a.mark_at ? new Date(a.mark_at).getTime() : 0;
          bValue = b.mark_at ? new Date(b.mark_at).getTime() : 0;
          break;
        default:
          aValue = a.id || 0;
          bValue = b.id || 0;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Attendance</h1>
          <p className="text-gray-600 mt-2">Mark and manage student attendance</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Search Bar with Options Icon */}
          <div className="relative" ref={optionsRef}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 pr-10 py-2 text-sm w-[250px] transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <button
                onClick={() => setShowOptions(!showOptions)}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded transition-all duration-200"
                title="Sort & Filter Options"
              >
                <Settings size={16} />
              </button>
            </div>

            {/* Options Dropdown */}
            {showOptions && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50 p-4 transition-all duration-200 transform origin-top-right opacity-100 scale-100">
                <div className="space-y-4">
                  {/* Sort Section */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="id">ID</option>
                      <option value="student">Student</option>
                      <option value="subject">Subject</option>
                      <option value="status">Status</option>
                      <option value="mark_at">Date</option>
                    </select>
                    <div className="mt-2">
                      <button
                        onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                        className="btn btn-secondary text-sm px-3 py-1.5 w-full transition-all duration-200 hover:scale-105"
                      >
                        {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
                      </button>
                    </div>
                  </div>

                  {/* Filter Section */}
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Subject</label>
                      <select
                        value={filterSubject}
                        onChange={(e) => setFilterSubject(e.target.value)}
                        className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="all">All Subjects</option>
                        {subjects.map((subject) => (
                          <option key={subject.id} value={subject.name}>
                            {subject.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Status</label>
                      <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="all">All Status</option>
                        <option value="present">Present</option>
                        <option value="absent">Absent</option>
                        <option value="late">Late</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button onClick={() => { resetForm(); setIsModalOpen(true); }} className="btn btn-primary flex items-center space-x-2">
            <Plus size={20} />
            <span>Mark Attendance</span>
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student</th>
              <th>Subject</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAttendance.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-500">No attendance records found</td>
              </tr>
            ) : (
              filteredAttendance.map((record) => (
                <tr key={record.id || Math.random()}>
                  <td>{record.id || 'N/A'}</td>
                  <td>{record.student || 'N/A'}</td>
                  <td>{record.subject || 'N/A'}</td>
                  <td>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status || 'present')}`}>
                      {record.status || 'N/A'}
                    </span>
                  </td>
                  <td>{record.mark_at ? new Date(record.mark_at).toLocaleDateString() : 'N/A'}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <button onClick={() => handleEdit(record)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                        <Edit size={18} />
                      </button>
                      <button onClick={() => handleDeleteClick(record)} className="p-2 text-red-600 hover:bg-red-50 rounded">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingAttendance ? 'Edit Attendance' : 'Mark Attendance'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Student</label>
            <select required value={formData.student_name} onChange={(e) => setFormData({ ...formData, student_name: e.target.value })} className="input">
              <option value="">Select a student</option>
              {students.map((student) => (
                <option key={student.id} value={student.name}>{student.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
            <select required value={formData.subject_name} onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })} className="input">
              <option value="">Select a subject</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.name}>{subject.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select required value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value as 'present' | 'absent' | 'late' })} className="input">
              <option value="present">Present</option>
              <option value="absent">Absent</option>
              <option value="late">Late</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingAttendance ? 'Update' : 'Mark'} Attendance</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingAttendance(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Attendance Record"
        itemName={`${deletingAttendance?.student || ''} - ${deletingAttendance?.subject || ''}`}
        itemType="attendance record"
        effects={[
          'This attendance record will be permanently removed',
          'Student attendance statistics will be affected',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default TeacherAttendance;

