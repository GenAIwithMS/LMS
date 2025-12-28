import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getResults, createResult, updateResult, deleteResult, getStudents, getSubjects } from '../../services/api';
import type { Result, Student, Subject } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

const TeacherResults: React.FC = () => {
  const [results, setResults] = useState<Result[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingResult, setEditingResult] = useState<Result | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingResult, setDeletingResult] = useState<Result | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterSubject, setFilterSubject] = useState('all');
  const optionsRef = useRef<HTMLDivElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    student_name: '',
    subject_name: '',
    total_marks: 100,
    obtained_marks: 0,
    exam_type: '',
    remarks: '',
  });

  useEffect(() => {
    fetchResults();
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

  const fetchResults = async () => {
    try {
      setLoading(true);
      console.log('Fetching results...');
      const data = await getResults();
      console.log('Results API response:', data);
      
      // Handle different response formats
      let resultsData: Result[] = [];
      
      if (Array.isArray(data)) {
        resultsData = data;
      } else if (data && Array.isArray(data.results)) {
        resultsData = data.results;
      } else if (data && data.result) {
        resultsData = Array.isArray(data.result) ? data.result : [data.result];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const resultsArray = Object.values(data).find((val) => Array.isArray(val)) as Result[] | undefined;
        if (resultsArray) {
          resultsData = resultsArray;
        }
      }
      
      // Ensure all results have required fields with defaults
      resultsData = resultsData.map((result: any) => ({
        id: result.id || 0,
        student: result.student || result.student_name || '',
        subject: result.subject || result.subject_name || '',
        total_marks: result.total_marks || result.totalMarks || 100,
        obtained_marks: result.obtained_marks || result.obtainedMarks || 0,
        exam_type: result.exam_type || result.examType || '',
        remarks: result.remarks || '',
      }));
      
      console.log('Processed results:', resultsData);
      setResults(resultsData);
    } catch (error: any) {
      console.error('Error fetching results:', error);
      showError(error, 'Failed to fetch results');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      console.log('Fetching students for result modal...');
      const data = await getStudents();
      console.log('Students API response:', data);
      
      // Handle different response formats
      let studentsData: Student[] = [];
      
      if (Array.isArray(data)) {
        studentsData = data;
      } else if (data && Array.isArray(data.students)) {
        studentsData = data.students;
      } else if (data && data.student) {
        studentsData = Array.isArray(data.student) ? data.student : [data.student];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const studentsArray = Object.values(data).find((val) => Array.isArray(val)) as Student[] | undefined;
        if (studentsArray) {
          studentsData = studentsArray;
        }
      }
      
      // Ensure all students have required fields
      studentsData = studentsData.map((student: any) => ({
        id: student.id || 0,
        name: student.name || student.username || '',
        username: student.username || '',
        email: student.email || '',
        section: student.section || student.section_name || '',
      }));
      
      console.log('Processed students:', studentsData);
      setStudents(studentsData);
    } catch (error: any) {
      console.error('Failed to fetch students:', error);
      showError(error, 'Failed to fetch students');
      setStudents([]);
    }
  };

  const fetchSubjects = async () => {
    try {
      console.log('Fetching subjects for result modal...');
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
    
    // Validate form data
    if (!formData.student_name || !formData.subject_name || !formData.exam_type) {
      showError({ message: 'Please fill in all required fields' }, 'Validation failed');
      return;
    }
    
    // Ensure numeric fields are numbers
    const submitData = {
      student_name: formData.student_name.trim(),
      subject_name: formData.subject_name.trim(),
      total_marks: Number(formData.total_marks),
      obtained_marks: Number(formData.obtained_marks),
      exam_type: formData.exam_type.trim(),
      remarks: formData.remarks.trim() || '',
    };
    
    try {
      console.log('Submitting result form data:', submitData);
      if (editingResult) {
        console.log('Updating result:', editingResult.id);
        await updateResult(editingResult.id, submitData);
        showSuccess('Result updated successfully');
      } else {
        console.log('Creating new result...');
        const response = await createResult(submitData);
        console.log('Create result response:', response);
        showSuccess('Result created successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchResults();
    } catch (error: any) {
      console.error('Error creating/updating result:', error);
      showError(error, 'Failed to save result');
    }
  };

  const handleEdit = (result: Result) => {
    setEditingResult(result);
    setFormData({
      student_name: result.student || '',
      subject_name: result.subject || '',
      total_marks: result.total_marks || 100,
      obtained_marks: result.obtained_marks || 0,
      exam_type: result.exam_type || '',
      remarks: result.remarks || '',
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (result: Result) => {
    setDeletingResult(result);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingResult) return;
    
    setIsDeleting(true);
    try {
      await deleteResult(deletingResult.id);
      showSuccess('Result deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingResult(null);
      fetchResults();
    } catch (error: any) {
      showError(error, 'Failed to delete result');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ student_name: '', subject_name: '', total_marks: 100, obtained_marks: 0, exam_type: '', remarks: '' });
    setEditingResult(null);
  };

  const filteredResults = results
    .filter((result) => {
      const student = result?.student || '';
      const subject = result?.subject || '';
      const search = searchTerm.toLowerCase();
      const matchesSearch = student.toLowerCase().includes(search) || subject.toLowerCase().includes(search);
      const matchesSubject = filterSubject === 'all' || result.subject === filterSubject;
      return matchesSearch && matchesSubject;
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
        case 'obtained_marks':
          aValue = a.obtained_marks || 0;
          bValue = b.obtained_marks || 0;
          break;
        case 'total_marks':
          aValue = a.total_marks || 0;
          bValue = b.total_marks || 0;
          break;
        case 'percentage':
          aValue = a.total_marks > 0 ? ((a.obtained_marks || 0) / a.total_marks) * 100 : 0;
          bValue = b.total_marks > 0 ? ((b.obtained_marks || 0) / b.total_marks) * 100 : 0;
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

  const calculatePercentage = (obtained: number, total: number) => {
    return total > 0 ? ((obtained / total) * 100).toFixed(1) : '0';
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
          <h1 className="text-3xl font-bold text-gray-900">Results</h1>
          <p className="text-gray-600 mt-2">Create and manage student results</p>
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
                      <option value="obtained_marks">Obtained Marks</option>
                      <option value="total_marks">Total Marks</option>
                      <option value="percentage">Percentage</option>
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
            <span>Create Result</span>
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
              <th>Marks</th>
              <th>Percentage</th>
              <th>Exam Type</th>
              <th>Remarks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-gray-500">No results found</td>
              </tr>
            ) : (
              filteredResults.map((result) => (
                <tr key={result.id || Math.random()}>
                  <td>{result.id || 'N/A'}</td>
                  <td>{result.student || 'N/A'}</td>
                  <td>{result.subject || 'N/A'}</td>
                  <td>{result.obtained_marks || 0} / {result.total_marks || 100}</td>
                  <td>{calculatePercentage(result.obtained_marks || 0, result.total_marks || 100)}%</td>
                  <td>{result.exam_type || 'N/A'}</td>
                  <td>{result.remarks || 'N/A'}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <button onClick={() => handleEdit(result)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                        <Edit size={18} />
                      </button>
                      <button onClick={() => handleDeleteClick(result)} className="p-2 text-red-600 hover:bg-red-50 rounded">
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

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingResult ? 'Edit Result' : 'Create Result'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Student</label>
            <select required value={formData.student_name} onChange={(e) => setFormData({ ...formData, student_name: e.target.value })} className="input" disabled={!!editingResult}>
              <option value="">Select a student</option>
              {students.length === 0 ? (
                <option value="" disabled>No students available</option>
              ) : (
                students.map((student) => (
                  <option key={student.id} value={student.name}>{student.name}</option>
                ))
              )}
            </select>
            {students.length === 0 && (
              <p className="text-xs text-red-600 mt-1">No students found. Please add students first.</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
            <select required value={formData.subject_name} onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })} className="input" disabled={!!editingResult}>
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Total Marks</label>
              <input type="number" required value={formData.total_marks} onChange={(e) => setFormData({ ...formData, total_marks: parseInt(e.target.value) })} className="input" min="1" disabled={!!editingResult} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Obtained Marks</label>
              <input type="number" required value={formData.obtained_marks} onChange={(e) => setFormData({ ...formData, obtained_marks: parseInt(e.target.value) })} className="input" min="0" max={formData.total_marks} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Exam Type</label>
            <input type="text" required value={formData.exam_type} onChange={(e) => setFormData({ ...formData, exam_type: e.target.value })} className="input" placeholder="e.g., midterm, final" disabled={!!editingResult} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Remarks</label>
            <textarea value={formData.remarks} onChange={(e) => setFormData({ ...formData, remarks: e.target.value })} className="input" rows={3} />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingResult ? 'Update' : 'Create'} Result</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingResult(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Result"
        itemName={`${deletingResult?.student || ''} - ${deletingResult?.subject || ''}`}
        itemType="result"
        effects={[
          'This result will be permanently removed',
          'Student performance data will be affected',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default TeacherResults;

