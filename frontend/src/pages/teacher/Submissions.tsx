import React, { useState, useEffect, useRef } from 'react';
import { Search, Edit, Download, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { getSubmissionsByAssignment, updateSubmission, getAssignments } from '../../services/api';
import type { Submission, Assignment } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';
import { useSearchParams } from 'react-router-dom';

const TeacherSubmissions: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(false);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSubmission, setEditingSubmission] = useState<Submission | null>(null);
  const [showOptions, setShowOptions] = useState(false);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const optionsRef = useRef<HTMLDivElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAssignment, setSelectedAssignment] = useState<number | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    marks_obtained: 0,
    feedback: '',
  });

  useEffect(() => {
    let isMounted = true;
    
    const loadAssignments = async () => {
      try {
        await fetchAssignments();
      } catch (error) {
        if (isMounted) {
          console.error('Error loading assignments:', error);
        }
      }
    };
    
    loadAssignments();
    
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (assignments.length > 0 && !selectedAssignment) {
      const assignmentId = searchParams.get('assignmentId');
      if (assignmentId) {
        const id = parseInt(assignmentId);
        if (!isNaN(id) && id > 0) {
          setSelectedAssignment(id);
        }
      } else {
        // Auto-select first assignment if available and no assignment is selected
        const firstAssignment = assignments[0];
        if (firstAssignment && firstAssignment.id) {
          const id = firstAssignment.id;
          setSelectedAssignment(id);
          setSearchParams({ assignmentId: id.toString() }, { replace: true });
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assignments]);

  useEffect(() => {
    if (selectedAssignment && selectedAssignment > 0) {
      console.log('Selected assignment changed, fetching submissions for:', selectedAssignment);
      fetchSubmissions();
    } else {
      console.log('No valid assignment selected, clearing submissions');
      setSubmissions([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAssignment]);

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

  const fetchSubmissions = async () => {
    if (!selectedAssignment) {
      setSubmissions([]);
      setSubmissionsLoading(false);
      return;
    }
    try {
      setSubmissionsLoading(true);
      console.log('Fetching submissions for assignment:', selectedAssignment);
      const response = await getSubmissionsByAssignment(selectedAssignment);
      console.log('Submissions API raw response:', response);
      console.log('Response type:', typeof response);
      console.log('Is array:', Array.isArray(response));
      console.log('Response keys:', response && typeof response === 'object' ? Object.keys(response) : 'N/A');
      
      // Handle different response formats
      let submissionsData: Submission[] = [];
      
      if (Array.isArray(response)) {
        // Direct array response
        submissionsData = response;
        console.log('Using direct array format');
      } else if (response && typeof response === 'object' && response !== null) {
        // Object response - check for data field first
        if (Array.isArray(response.data)) {
          submissionsData = response.data;
          console.log('Using data.data format, count:', submissionsData.length);
        } else if (Array.isArray(response.submissions)) {
          submissionsData = response.submissions;
          console.log('Using data.submissions format');
        } else if (response.submission) {
          submissionsData = Array.isArray(response.submission) ? response.submission : [response.submission];
          console.log('Using data.submission format');
        } else {
          // Try to find any array in the response
          const submissionsArray = Object.values(response).find((val) => Array.isArray(val)) as Submission[] | undefined;
          if (submissionsArray) {
            submissionsData = submissionsArray;
            console.log('Found array in response values');
          } else {
            // If it's a single object, wrap it in an array
            submissionsData = [response];
            console.log('Wrapping single object in array');
          }
        }
      }
      
      console.log('Raw submissions data before mapping:', submissionsData);
      
      // Ensure all submissions have required fields
      submissionsData = submissionsData.map((submission: any) => {
        const mapped = {
          id: submission.id || submission.submission_id || 0,
          student: submission.student || submission.student_name || submission.studentName || submission.username || `Student ${submission.student_id || ''}`,
          assignment: submission.assignment || submission.assignment_id || submission.assignmentId || selectedAssignment,
          submission_text: submission.submission_text || submission.submissionText || submission.submission || submission.text || '',
          submitted_at: submission.submitted_at || submission.submittedAt || submission.date || submission.created_at || submission.createdAt || new Date().toISOString(),
          marks_obtained: submission.marks_obtained !== undefined && submission.marks_obtained !== null ? submission.marks_obtained : (submission.marks !== undefined && submission.marks !== null ? submission.marks : (submission.marksObtained !== undefined && submission.marksObtained !== null ? submission.marksObtained : null)),
          feedback: submission.feedback || '',
        };
        console.log('Mapped submission:', mapped);
        return mapped;
      });
      
      // Only filter out truly invalid submissions (no ID at all)
      submissionsData = submissionsData.filter((sub) => {
        const isValid = sub.id > 0;
        if (!isValid) {
          console.log('Filtered out invalid submission:', sub);
        }
        return isValid;
      });
      
      console.log('Final processed submissions:', submissionsData);
      console.log('Number of submissions after processing:', submissionsData.length);
      setSubmissions(submissionsData);
    } catch (error: any) {
      console.error('Error fetching submissions:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
      showError(error, 'Failed to fetch submissions');
      setSubmissions([]);
    } finally {
      setSubmissionsLoading(false);
    }
  };

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      console.log('Starting to fetch assignments...');
      
      // Add timeout handling
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 35000); // 35 seconds
      });
      
      const data = await Promise.race([
        getAssignments(),
        timeoutPromise
      ]) as any;
      
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
      
      // Ensure all assignments have required fields
      assignmentsData = assignmentsData.map((assignment: any) => ({
        id: assignment.id || 0,
        title: assignment.title || '',
        description: assignment.description || '',
        due_date: assignment.due_date || assignment.dueDate || '',
        subject: assignment.subject || assignment.subject_name || '',
        total_marks: assignment.total_marks || assignment.totalMarks || 100,
      }));
      
      console.log('Processed assignments:', assignmentsData);
      setAssignments(assignmentsData);
    } catch (error: any) {
      console.error('Error fetching assignments:', error);
      if (error.message === 'Request timeout' || error.code === 'ECONNABORTED') {
        showError(new Error('The request took too long. Please check if the backend is running and try again.'), 'Request timeout');
      } else {
        showError(error, 'Failed to fetch assignments');
      }
      setAssignments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingSubmission) return;
    try {
      await updateSubmission(editingSubmission.id, formData);
      showSuccess('Submission updated successfully');
      setIsModalOpen(false);
      resetForm();
      fetchSubmissions();
    } catch (error: any) {
      showError(error, 'Failed to update submission');
    }
  };

  const handleEdit = (submission: Submission) => {
    setEditingSubmission(submission);
    setFormData({
      marks_obtained: submission.marks_obtained || 0,
      feedback: submission.feedback || '',
    });
    setIsModalOpen(true);
  };

  const resetForm = () => {
    setFormData({ marks_obtained: 0, feedback: '' });
    setEditingSubmission(null);
  };

  const filteredSubmissions = submissions
    .filter((submission) => {
      const student = submission.student?.toLowerCase() || '';
      const submissionText = submission.submission_text?.toLowerCase() || '';
      const search = searchTerm.toLowerCase();
      return student.includes(search) || submissionText.includes(search);
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'student':
          aValue = (a.student || '').toLowerCase();
          bValue = (b.student || '').toLowerCase();
          break;
        case 'submitted_at':
          aValue = a.submitted_at ? new Date(a.submitted_at).getTime() : 0;
          bValue = b.submitted_at ? new Date(b.submitted_at).getTime() : 0;
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
          <h1 className="text-3xl font-bold text-gray-900">Submissions</h1>
          <p className="text-gray-600 mt-2">Review and grade student submissions</p>
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
                      <option value="submitted_at">Submitted Date</option>
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
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {!selectedAssignment && assignments.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No assignments available</p>
        </div>
      ) : submissionsLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Student</th>
                <th>Submission Text</th>
                <th>Submitted At</th>
                <th>Marks</th>
                <th>Feedback</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredSubmissions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-500">
                    {selectedAssignment ? 'No submissions found for this assignment' : 'Please wait while assignments load...'}
                  </td>
                </tr>
              ) : (
                filteredSubmissions.map((submission) => (
                  <tr key={submission.id}>
                    <td>{submission.id}</td>
                    <td>{submission.student || 'N/A'}</td>
                    <td className="max-w-xs truncate">{submission.submission_text || 'N/A'}</td>
                    <td>{submission.submitted_at ? new Date(submission.submitted_at).toLocaleDateString() : 'N/A'}</td>
                    <td>{submission.marks_obtained !== null && submission.marks_obtained !== undefined ? submission.marks_obtained : 'Not graded'}</td>
                    <td className="max-w-xs truncate">{submission.feedback || 'N/A'}</td>
                    <td>
                      <button
                        onClick={() => handleEdit(submission)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <Edit size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
        title="Grade Submission"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Marks Obtained</label>
            <input
              type="number"
              required
              value={formData.marks_obtained}
              onChange={(e) => setFormData({ ...formData, marks_obtained: parseInt(e.target.value) })}
              className="input"
              min="0"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Feedback</label>
            <textarea
              value={formData.feedback}
              onChange={(e) => setFormData({ ...formData, feedback: e.target.value })}
              className="input"
              rows={4}
            />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setIsModalOpen(false);
                resetForm();
              }}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Update Grade
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default TeacherSubmissions;

