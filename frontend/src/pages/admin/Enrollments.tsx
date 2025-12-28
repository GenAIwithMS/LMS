import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getEnrollments, enrollStudent, updateEnrollment, deleteEnrollment, getStudents, getCourses } from '../../services/api';
import type { Enrollment, Student, Course } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

// Utility function to format date from database
const formatDate = (dateString: string | undefined | null): string => {
  if (!dateString) return 'N/A';
  
  try {
    // Handle GMT date strings like "Sun, 28 Dec 2025 00:00:00 GMT"
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';
    
    // Format as YYYY-MM-DD
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch (error) {
    // If it's already in YYYY-MM-DD format, return as is
    if (typeof dateString === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
      return dateString;
    }
    return 'N/A';
  }
};

const AdminEnrollments: React.FC = () => {
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEnrollment, setEditingEnrollment] = useState<Enrollment | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterCourse, setFilterCourse] = useState<string>('all');
  const [showOptions, setShowOptions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingEnrollment, setDeletingEnrollment] = useState<Enrollment | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const optionsRef = useRef<HTMLDivElement>(null);
  const [formData, setFormData] = useState({
    student_name: '',
    course_name: '',
    enrollment_date: '',
    status: 'active',
    grade: '',
  });

  const fetchEnrollments = async () => {
    console.log('fetchEnrollments called');
    try {
      setLoading(true);
      console.log('Calling getEnrollments API...');
      const data = await getEnrollments();
      console.log('Enrollments API response:', data);
      
      // Handle different response formats
      let enrollmentsData: Enrollment[] = [];
      
      if (Array.isArray(data)) {
        enrollmentsData = data;
      } else if (data && Array.isArray(data.enrollments)) {
        enrollmentsData = data.enrollments;
      } else if (data && data.enrollment) {
        enrollmentsData = Array.isArray(data.enrollment) ? data.enrollment : [data.enrollment];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const enrollmentsArray = Object.values(data).find((val) => Array.isArray(val)) as Enrollment[] | undefined;
        if (enrollmentsArray) {
          enrollmentsData = enrollmentsArray;
        }
      }
      
      // Ensure all enrollments have required fields with defaults
      enrollmentsData = enrollmentsData.map((enrollment: any) => ({
        id: enrollment.id || 0,
        student: enrollment.student || enrollment.student_name || '',
        course: enrollment.course || enrollment.course_name || '',
        enrollment_date: enrollment.enrollment_date || enrollment.enrollmentDate || '',
        status: enrollment.status || 'active',
        grade: enrollment.grade || '',
      }));
      
      console.log('Processed enrollments:', enrollmentsData);
      setEnrollments(enrollmentsData);
    } catch (error: any) {
      console.error('Error fetching enrollments:', error);
      showError(error, 'Failed to fetch enrollments');
      setEnrollments([]);
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

  const fetchCourses = async () => {
    try {
      const data = await getCourses();
      setCourses(Array.isArray(data) ? data : data.course ? [data.course] : []);
    } catch (error) {
      console.error('Failed to fetch courses');
    }
  };

  useEffect(() => {
    console.log('AdminEnrollments component mounted, fetching data...');
    fetchEnrollments();
    fetchStudents();
    fetchCourses();
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Prepare data, only include enrollment_date if it's provided
      const submitData: any = {
        student_name: formData.student_name,
        course_name: formData.course_name,
        status: formData.status,
        grade: formData.grade,
      };
      
      // Only include enrollment_date if it's not empty
      if (formData.enrollment_date && formData.enrollment_date.trim() !== '') {
        submitData.enrollment_date = formData.enrollment_date;
      }
      
      if (editingEnrollment) {
        await updateEnrollment(editingEnrollment.id, submitData);
        showSuccess('Enrollment updated successfully');
      } else {
        await enrollStudent(submitData);
        showSuccess('Student enrolled successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchEnrollments();
    } catch (error: any) {
      showError(error, 'Failed to save enrollment');
    }
  };

  const handleEdit = (enrollment: Enrollment) => {
    setEditingEnrollment(enrollment);
    // Format the date for the input field (YYYY-MM-DD format)
    const formattedDate = formatDate(enrollment.enrollment_date);
    setFormData({
      student_name: enrollment.student,
      course_name: enrollment.course,
      enrollment_date: formattedDate !== 'N/A' ? formattedDate : '',
      status: enrollment.status,
      grade: enrollment.grade,
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (enrollment: Enrollment) => {
    setDeletingEnrollment(enrollment);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingEnrollment) return;
    
    setIsDeleting(true);
    try {
      await deleteEnrollment(deletingEnrollment.id);
      showSuccess('Enrollment deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingEnrollment(null);
      fetchEnrollments();
    } catch (error: any) {
      showError(error, 'Failed to delete enrollment');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ student_name: '', course_name: '', enrollment_date: '', status: 'active', grade: '' });
    setEditingEnrollment(null);
  };

  const filteredEnrollments = enrollments
    .filter((enrollment) => {
      // Search filter
      const student = enrollment?.student || '';
      const course = enrollment?.course || '';
      const search = searchTerm.toLowerCase();
      const matchesSearch = student.toLowerCase().includes(search) || course.toLowerCase().includes(search);
      
      // Status filter
      const matchesStatus = filterStatus === 'all' || enrollment.status === filterStatus;
      
      // Course filter
      const matchesCourse = filterCourse === 'all' || enrollment.course === filterCourse;
      
      return matchesSearch && matchesStatus && matchesCourse;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;
      
      switch (sortBy) {
        case 'student':
          aValue = (a.student || '').toLowerCase();
          bValue = (b.student || '').toLowerCase();
          break;
        case 'course':
          aValue = (a.course || '').toLowerCase();
          bValue = (b.course || '').toLowerCase();
          break;
        case 'date':
          aValue = a.enrollment_date ? new Date(a.enrollment_date).getTime() : 0;
          bValue = b.enrollment_date ? new Date(b.enrollment_date).getTime() : 0;
          break;
        case 'status':
          aValue = (a.status || '').toLowerCase();
          bValue = (b.status || '').toLowerCase();
          break;
        case 'grade':
          aValue = (a.grade || '').toLowerCase();
          bValue = (b.grade || '').toLowerCase();
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="pl-2">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Enrollments</h1>
          <p className="text-gray-600 mt-2">Manage student enrollments</p>
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
                      <option value="course">Course</option>
                      <option value="date">Date</option>
                      <option value="status">Status</option>
                      <option value="grade">Grade</option>
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
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Status</label>
                    <select 
                      value={filterStatus} 
                      onChange={(e) => setFilterStatus(e.target.value)} 
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="all">All Status</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Course</label>
                    <select 
                      value={filterCourse} 
                      onChange={(e) => setFilterCourse(e.target.value)} 
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="all">All Courses</option>
                      {courses.map((course) => (
                        <option key={course.id} value={course.name}>
                          {course.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button onClick={() => { resetForm(); setIsModalOpen(true); }} className="btn btn-primary flex items-center space-x-2">
            <Plus size={20} />
            <span>Enroll Student</span>
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Student</th>
              <th>Course</th>
              <th>Enrollment Date</th>
              <th>Status</th>
              <th>Grade</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEnrollments.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-500">No enrollments found</td>
              </tr>
            ) : (
              filteredEnrollments.map((enrollment) => (
                <tr key={enrollment.id || Math.random()}>
                  <td>{enrollment.id || 'N/A'}</td>
                  <td>{enrollment.student || 'N/A'}</td>
                  <td>{enrollment.course || 'N/A'}</td>
                  <td>{formatDate(enrollment.enrollment_date)}</td>
                  <td>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      enrollment.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {enrollment.status || 'N/A'}
                    </span>
                  </td>
                  <td>{enrollment.grade || 'N/A'}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <button onClick={() => handleEdit(enrollment)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                        <Edit size={18} />
                      </button>
                      <button onClick={() => handleDeleteClick(enrollment)} className="p-2 text-red-600 hover:bg-red-50 rounded">
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

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingEnrollment ? 'Edit Enrollment' : 'Enroll Student'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Student</label>
            <select required value={formData.student_name} onChange={(e) => setFormData({ ...formData, student_name: e.target.value })} className="input" disabled={!!editingEnrollment}>
              <option value="">Select a student</option>
              {students.map((student) => (
                <option key={student.id} value={student.name}>{student.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Course</label>
            <select required value={formData.course_name} onChange={(e) => setFormData({ ...formData, course_name: e.target.value })} className="input" disabled={!!editingEnrollment}>
              <option value="">Select a course</option>
              {courses.map((course) => (
                <option key={course.id} value={course.name}>{course.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Enrollment Date (Optional)</label>
            <input type="date" value={formData.enrollment_date} onChange={(e) => setFormData({ ...formData, enrollment_date: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select required value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} className="input">
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Grade</label>
            <input type="text" value={formData.grade} onChange={(e) => setFormData({ ...formData, grade: e.target.value })} className="input" placeholder="e.g., A, B, C" />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingEnrollment ? 'Update' : 'Enroll'} Student</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingEnrollment(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Enrollment"
        itemName={`${deletingEnrollment?.student || ''} - ${deletingEnrollment?.course || ''}`}
        itemType="enrollment"
        effects={[
          'Student will be unenrolled from this course',
          'All related course data for this student will be removed',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default AdminEnrollments;

