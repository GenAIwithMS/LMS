import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Eye, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getAssignments, createAssignment, updateAssignment, deleteAssignment, getSubjects } from '../../services/api';
import type { Assignment, Subject } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const TeacherAssignments: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<Assignment | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingAssignment, setDeletingAssignment] = useState<Assignment | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterSubject, setFilterSubject] = useState('all');
  const optionsRef = useRef<HTMLDivElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
    subject_name: '',
    total_marks: 100,
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchAssignments();
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

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      console.log('Fetching assignments...');
      const data = await getAssignments();
      console.log('Assignments API response:', data);
      
      // Handle different response formats
      let assignmentsData: Assignment[] = [];
      
      if (Array.isArray(data)) {
        assignmentsData = data;
      } else if (data && Array.isArray(data.assignments)) {
        assignmentsData = data.assignments;
      } else if (data && data.assignment) {
        assignmentsData = Array.isArray(data.assignment) ? data.assignment : [data.assignment];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const assignmentsArray = Object.values(data).find((val) => Array.isArray(val)) as Assignment[] | undefined;
        if (assignmentsArray) {
          assignmentsData = assignmentsArray;
        }
      }
      
      // Ensure all assignments have required fields with defaults
      assignmentsData = assignmentsData.map((assignment: any) => ({
        id: assignment.id || 0,
        title: assignment.title || '',
        description: assignment.description || '',
        due_date: assignment.due_date || assignment.dueDate || '',
        subject: assignment.subject || assignment.subject_name || '',
        teacher: assignment.teacher || assignment.teacher_name || '',
        total_marks: assignment.total_marks || assignment.totalMarks || 100,
      }));
      
      console.log('Processed assignments:', assignmentsData);
      setAssignments(assignmentsData);
    } catch (error: any) {
      console.error('Error fetching assignments:', error);
      showError(error, 'Failed to fetch assignments');
      setAssignments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubjects = async () => {
    try {
      console.log('Fetching subjects for assignment modal...');
      const data = await getSubjects();
      console.log('Subjects API response:', data);
      
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
      console.error('Failed to fetch subjects:', error);
      showError(error, 'Failed to fetch subjects');
      setSubjects([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAssignment) {
        await updateAssignment(editingAssignment.id, formData);
        showSuccess('Assignment updated successfully');
      } else {
        await createAssignment(formData);
        showSuccess('Assignment created successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchAssignments();
    } catch (error: any) {
      showError(error, 'Failed to save assignment');
    }
  };

  const handleEdit = (assignment: Assignment) => {
    setEditingAssignment(assignment);
    setFormData({
      title: assignment.title,
      description: assignment.description,
      due_date: assignment.due_date,
      subject_name: assignment.subject,
      total_marks: assignment.total_marks,
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (assignment: Assignment) => {
    setDeletingAssignment(assignment);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingAssignment) return;
    
    setIsDeleting(true);
    try {
      await deleteAssignment(deletingAssignment.id);
      showSuccess('Assignment deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingAssignment(null);
      fetchAssignments();
    } catch (error: any) {
      showError(error, 'Failed to delete assignment');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ title: '', description: '', due_date: '', subject_name: '', total_marks: 100 });
    setEditingAssignment(null);
  };

  const filteredAssignments = assignments
    .filter((assignment) => {
      const title = assignment?.title || '';
      const subject = assignment?.subject || '';
      const search = searchTerm.toLowerCase();
      const matchesSearch = title.toLowerCase().includes(search) || subject.toLowerCase().includes(search);
      const matchesSubject = filterSubject === 'all' || assignment.subject === filterSubject;
      return matchesSearch && matchesSubject;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'title':
          aValue = (a.title || '').toLowerCase();
          bValue = (b.title || '').toLowerCase();
          break;
        case 'subject':
          aValue = (a.subject || '').toLowerCase();
          bValue = (b.subject || '').toLowerCase();
          break;
        case 'due_date':
          aValue = a.due_date || '';
          bValue = b.due_date || '';
          break;
        case 'total_marks':
          aValue = a.total_marks || 0;
          bValue = b.total_marks || 0;
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
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-2">Create and manage assignments</p>
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
                      <option value="title">Title</option>
                      <option value="subject">Subject</option>
                      <option value="due_date">Due Date</option>
                      <option value="total_marks">Total Marks</option>
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
                </div>
              </div>
            )}
          </div>

          <button onClick={() => { resetForm(); setIsModalOpen(true); }} className="btn btn-primary flex items-center space-x-2">
            <Plus size={20} />
            <span>Create Assignment</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAssignments.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No assignments found</div>
        ) : (
          filteredAssignments.map((assignment) => (
            <div key={assignment.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{assignment.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{assignment.subject}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button onClick={() => navigate(`/teacher/submissions?assignmentId=${assignment.id}`)} className="p-2 text-green-600 hover:bg-green-50 rounded" title="View Submissions">
                    <Eye size={18} />
                  </button>
                  <button onClick={() => handleEdit(assignment)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                    <Edit size={18} />
                  </button>
                  <button onClick={() => handleDeleteClick(assignment)} className="p-2 text-red-600 hover:bg-red-50 rounded">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              <p className="text-gray-600 mb-4 line-clamp-2">{assignment.description}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Due: {assignment.due_date}</span>
                <span className="font-medium text-gray-900">{assignment.total_marks} marks</span>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingAssignment ? 'Edit Assignment' : 'Create Assignment'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea required value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="input" rows={4} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
            <select required value={formData.subject_name} onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })} className="input">
              <option value="">Select a subject</option>
              {subjects.length === 0 ? (
                <option value="" disabled>No subjects available</option>
              ) : (
                subjects.map((subject) => (
                  <option key={subject.id} value={subject.name}>{subject.name}</option>
                ))
              )}
            </select>
            {subjects.length === 0 && (
              <p className="text-xs text-red-600 mt-1">No subjects found. Please create subjects first.</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
              <input type="date" required value={formData.due_date} onChange={(e) => setFormData({ ...formData, due_date: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Total Marks</label>
              <input type="number" required value={formData.total_marks} onChange={(e) => setFormData({ ...formData, total_marks: parseInt(e.target.value) })} className="input" min="1" />
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingAssignment ? 'Update' : 'Create'} Assignment</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingAssignment(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Assignment"
        itemName={deletingAssignment?.title || ''}
        itemType="assignment"
        effects={[
          'All student submissions for this assignment',
          'All grades and feedback for this assignment',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default TeacherAssignments;

