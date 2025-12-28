import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getCourses, addCourse, updateCourse, deleteCourse, getTeachers } from '../../services/api';
import type { Course, Teacher } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

const AdminCourses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterTeacher, setFilterTeacher] = useState<string>('all');
  const [showOptions, setShowOptions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingCourse, setDeletingCourse] = useState<Course | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const optionsRef = useRef<HTMLDivElement>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    course_code: '',
    teacher_name: '',
    created_at: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchCourses();
    fetchTeachers();
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

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await getCourses();
      console.log('Courses API raw response:', data);
      
      // Handle different response formats
      let coursesData: Course[] = [];
      
      if (Array.isArray(data)) {
        coursesData = data;
      } else if (data && Array.isArray(data.courses)) {
        coursesData = data.courses;
      } else if (data && data.course) {
        coursesData = Array.isArray(data.course) ? data.course : [data.course];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const coursesArray = Object.values(data).find((val) => Array.isArray(val)) as Course[] | undefined;
        if (coursesArray) {
          coursesData = coursesArray;
        }
      }
      
      // Ensure all courses have required fields with proper teacher mapping
      coursesData = coursesData.map((course: any) => ({
        id: course.id || 0,
        name: course.name || '',
        description: course.description || '',
        course_code: course.course_code || course.courseCode || '',
        teacher: course.teacher || course.teacher_name || '',
      }));
      
      console.log('Courses after processing:', coursesData);
      setCourses(coursesData);
    } catch (error: any) {
      console.error('Error fetching courses:', error);
      showError(error, 'Failed to fetch courses');
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTeachers = async () => {
    try {
      const data = await getTeachers();
      setTeachers(Array.isArray(data) ? data : data.teacher ? [data.teacher] : []);
    } catch (error) {
      console.error('Failed to fetch teachers');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCourse) {
        await updateCourse(editingCourse.id, formData);
        showSuccess('Course updated successfully');
      } else {
        await addCourse(formData);
        showSuccess('Course added successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchCourses();
    } catch (error: any) {
      showError(error, 'Failed to save course');
    }
  };

  const handleEdit = (course: Course) => {
    setEditingCourse(course);
    setFormData({
      name: course.name,
      description: course.description,
      course_code: course.course_code,
      teacher_name: course.teacher,
      created_at: new Date().toISOString().split('T')[0],
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (course: Course) => {
    setDeletingCourse(course);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingCourse) return;
    
    setIsDeleting(true);
    try {
      await deleteCourse(deletingCourse.id);
      showSuccess('Course deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingCourse(null);
      fetchCourses();
    } catch (error: any) {
      showError(error, 'Failed to delete course');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ name: '', description: '', course_code: '', teacher_name: '', created_at: new Date().toISOString().split('T')[0] });
    setEditingCourse(null);
  };

  const filteredCourses = courses
    .filter((course) => {
      const matchesSearch =
        course.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.course_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.description?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTeacher = filterTeacher === 'all' || course.teacher === filterTeacher;
      return matchesSearch && matchesTeacher;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'name':
          aValue = (a.name || '').toLowerCase();
          bValue = (b.name || '').toLowerCase();
          break;
        case 'code':
          aValue = (a.course_code || '').toLowerCase();
          bValue = (b.course_code || '').toLowerCase();
          break;
        case 'teacher':
          aValue = (a.teacher || '').toLowerCase();
          bValue = (b.teacher || '').toLowerCase();
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
          <h1 className="text-3xl font-bold text-gray-900">Courses</h1>
          <p className="text-gray-600 mt-2">Manage all courses in the system</p>
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
                      <option value="name">Name</option>
                      <option value="code">Course Code</option>
                      <option value="teacher">Teacher</option>
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
                    <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Teacher</label>
                    <select
                      value={filterTeacher}
                      onChange={(e) => setFilterTeacher(e.target.value)}
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="all">All Teachers</option>
                      {teachers.map((teacher) => (
                        <option key={teacher.id} value={teacher.name}>
                          {teacher.name}
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
            <span>Add Course</span>
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Code</th>
              <th>Description</th>
              <th>Teacher</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCourses.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-500">No courses found</td>
              </tr>
            ) : (
              filteredCourses.map((course) => (
                <tr key={course.id}>
                  <td>{course.id}</td>
                  <td>{course.name}</td>
                  <td>{course.course_code}</td>
                  <td className="max-w-xs truncate">{course.description}</td>
                  <td>{course.teacher}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <button onClick={() => handleEdit(course)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                        <Edit size={18} />
                      </button>
                      <button onClick={() => handleDeleteClick(course)} className="p-2 text-red-600 hover:bg-red-50 rounded">
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

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingCourse ? 'Edit Course' : 'Add Course'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input type="text" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Course Code</label>
            <input type="text" required value={formData.course_code} onChange={(e) => setFormData({ ...formData, course_code: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea required value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="input" rows={3} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Teacher</label>
            <select required value={formData.teacher_name} onChange={(e) => setFormData({ ...formData, teacher_name: e.target.value })} className="input">
              <option value="">Select a teacher</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.name}>{teacher.name}</option>
              ))}
            </select>
          </div>
          {!editingCourse && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Created At</label>
              <input type="date" required value={formData.created_at} onChange={(e) => setFormData({ ...formData, created_at: e.target.value })} className="input" />
            </div>
          )}
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingCourse ? 'Update' : 'Add'} Course</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingCourse(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Course"
        itemName={deletingCourse?.name || ''}
        itemType="course"
        effects={[
          'All assignments associated with this course',
          'All enrolled students in this course',
          'All subjects linked to this course',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default AdminCourses;

