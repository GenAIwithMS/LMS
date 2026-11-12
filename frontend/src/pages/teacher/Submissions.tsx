import React, { useState, useEffect, useRef } from 'react';
import { Search, Edit, Download, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { getSubmissionsByAssignment, updateSubmission, getAssignments, downloadSubmissionFile } from '../../services/api';
import type { Submission, Assignment } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';
import { useSearchParams } from 'react-router-dom';

// An assignment as listed in the picker: it also knows its section
interface SectionAssignment extends Assignment {
  section_name: string | null;
}

// Marks without needless decimals: "10" instead of "10.00", but "7.5" stays
const marksText = (value: number | string): string => {
  const number = Number(value);
  if (isNaN(number)) {
    return String(value);
  }
  return String(number);
};

const TeacherSubmissions: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [assignments, setAssignments] = useState<SectionAssignment[]>([]);
  const [loading, setLoading] = useState(false);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSubmission, setEditingSubmission] = useState<Submission | null>(null);
  const [showOptions, setShowOptions] = useState(false);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const optionsRef = useRef<HTMLDivElement>(null);
  // The assignment whose submissions were asked for last. When the teacher
  // switches quickly, an older answer can arrive late; it is then ignored.
  const latestRequestRef = useRef<number | null>(null);
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

  // The assignment shown follows the address (?assignmentId=), so "View Submissions" on
  // another assignment, or the menu link, always shows the right one. Without a valid
  // one in the address, the first assignment is shown and written into the address.
  useEffect(() => {
    if (assignments.length === 0) {
      return;
    }
    const idText = searchParams.get('assignmentId');
    let id = idText ? parseInt(idText) : NaN;

    let found = false;
    for (const assignment of assignments) {
      if (assignment.id === id) {
        found = true;
      }
    }
    if (!found) {
      id = assignments[0].id;
      setSearchParams({ assignmentId: id.toString() }, { replace: true });
    }
    if (id !== selectedAssignment) {
      setSelectedAssignment(id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assignments, searchParams]);

  // The teacher picked another assignment in the picker
  const handleAssignmentChange = (value: string) => {
    const id = parseInt(value);
    if (isNaN(id)) {
      return;
    }
    setSearchParams({ assignmentId: id.toString() });
  };

  useEffect(() => {
    if (selectedAssignment && selectedAssignment > 0) {
      fetchSubmissions();
    } else {
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
    const requestedAssignment = selectedAssignment;
    latestRequestRef.current = requestedAssignment;
    try {
      setSubmissionsLoading(true);
      const response = await getSubmissionsByAssignment(requestedAssignment);

      // The teacher picked another assignment while this one was loading
      if (latestRequestRef.current !== requestedAssignment) {
        return;
      }

      // Handle different response formats
      let submissionsData: Submission[] = [];
      
      if (Array.isArray(response)) {
        // Direct array response
        submissionsData = response;
      } else if (response && typeof response === 'object' && response !== null) {
        // Object response - check for data field first
        if (Array.isArray(response.data)) {
          submissionsData = response.data;
        } else if (Array.isArray(response.submissions)) {
          submissionsData = response.submissions;
        } else if (response.submission) {
          submissionsData = Array.isArray(response.submission) ? response.submission : [response.submission];
        } else {
          // Try to find any array in the response
          const submissionsArray = Object.values(response).find((val) => Array.isArray(val)) as Submission[] | undefined;
          if (submissionsArray) {
            submissionsData = submissionsArray;
          } else {
            // If it's a single object, wrap it in an array
            submissionsData = [response];
          }
        }
      }

      // Ensure all submissions have required fields
      submissionsData = submissionsData.map((submission: any) => {
        const mapped = {
          id: submission.id || submission.submission_id || 0,
          student: submission.student || submission.student_name || submission.studentName || submission.username || `Student ${submission.student_id || ''}`,
          assignment: submission.assignment || submission.assignment_id || submission.assignmentId || selectedAssignment,
          submission_text: submission.submission_text || submission.submissionText || submission.submission || submission.text || '',
          submission_file: submission.submission_file || '',
          submitted_at: submission.submitted_at || submission.submittedAt || submission.date || submission.created_at || submission.createdAt || new Date().toISOString(),
          marks_obtained: submission.marks_obtained !== undefined && submission.marks_obtained !== null ? submission.marks_obtained : (submission.marks !== undefined && submission.marks !== null ? submission.marks : (submission.marksObtained !== undefined && submission.marksObtained !== null ? submission.marksObtained : null)),
          feedback: submission.feedback || '',
        };
        return mapped;
      });
      
      // Only filter out truly invalid submissions (no ID at all)
      submissionsData = submissionsData.filter((sub) => sub.id > 0);
      
      setSubmissions(submissionsData);
    } catch (error: any) {
      if (latestRequestRef.current !== requestedAssignment) {
        return;
      }
      showError(error, 'Failed to fetch submissions');
      setSubmissions([]);
    } finally {
      if (latestRequestRef.current === requestedAssignment) {
        setSubmissionsLoading(false);
      }
    }
  };

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      
      // Add timeout handling
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 35000); // 35 seconds
      });
      
      const data = await Promise.race([
        getAssignments(),
        timeoutPromise
      ]) as any;

      // Handle different response formats
      let assignmentsData: SectionAssignment[] = [];
      
      if (Array.isArray(data)) {
        assignmentsData = data;
      } else if (data && Array.isArray(data.assignments)) {
        assignmentsData = data.assignments;
      } else if (data && data.assignment) {
        assignmentsData = Array.isArray(data.assignment) ? data.assignment : [data.assignment];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const assignmentsArray = Object.values(data).find((val) => Array.isArray(val)) as SectionAssignment[] | undefined;
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
        teacher: assignment.teacher || assignment.teacher_name || '',
        total_marks: assignment.total_marks || assignment.totalMarks || 100,
        section_name: assignment.section_name || null,
      }));
      
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
      marks_obtained: Number(submission.marks_obtained) || 0,
      feedback: submission.feedback || '',
    });
    setIsModalOpen(true);
  };

  const handleDownload = async (submission: Submission) => {
    try {
      await downloadSubmissionFile(submission.id);
    } catch (error: any) {
      toast.error('Could not download the file. It may have been removed.');
    }
  };

  const resetForm = () => {
    setFormData({ marks_obtained: 0, feedback: '' });
    setEditingSubmission(null);
  };

  // The assignment being shown, for its name and total marks
  let currentAssignment: SectionAssignment | null = null;
  for (const assignment of assignments) {
    if (assignment.id === selectedAssignment) {
      currentAssignment = assignment;
    }
  }

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
      {/* On a phone the title, search box and buttons stack, so nothing is pushed off the screen */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Submissions</h1>
          <p className="text-gray-600 mt-2">Review and grade student submissions</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Bar with Options Icon */}
          <div className="relative w-full sm:w-auto" ref={optionsRef}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 pr-10 py-2 text-sm w-full sm:w-[250px] transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
                        className="btn btn-secondary text-sm px-3 py-1.5 w-full transition-all duration-200"
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

      {/* Which assignment's submissions are shown, and a way to switch */}
      {assignments.length > 0 && (
        <div className="card mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Assignment</label>
          <select
            value={selectedAssignment !== null ? String(selectedAssignment) : ''}
            onChange={(e) => handleAssignmentChange(e.target.value)}
            className="input w-full sm:w-auto"
          >
            {assignments.map((assignment) => {
              const parts = [assignment.title];
              if (assignment.section_name) {
                parts.push(assignment.section_name);
              }
              if (assignment.subject) {
                parts.push(assignment.subject);
              }
              return (
                <option key={assignment.id} value={assignment.id}>
                  {parts.join(' · ')}
                </option>
              );
            })}
          </select>
          {currentAssignment && (
            <p className="text-sm text-gray-500 mt-2">Out of {marksText(currentAssignment.total_marks)} marks</p>
          )}
        </div>
      )}

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
                    <td>{submission.submitted_at ? new Date(submission.submitted_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'}</td>
                    <td>{submission.marks_obtained !== null && submission.marks_obtained !== undefined ? marksText(submission.marks_obtained) : 'Not graded'}</td>
                    <td className="max-w-xs truncate">{submission.feedback || 'N/A'}</td>
                    <td>
                      <div className="flex items-center space-x-1">
                        {submission.submission_file && (
                          <button
                            onClick={() => handleDownload(submission)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded"
                            title="Download file"
                          >
                            <Download size={18} />
                          </button>
                        )}
                        <button
                          onClick={() => handleEdit(submission)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                          title="Check and grade"
                        >
                          <Edit size={18} />
                        </button>
                      </div>
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
        title="Check & Grade Submission"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* The student's work, so the teacher can read it before grading */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Submitted by {editingSubmission?.student || 'student'}
            </label>
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg max-h-60 overflow-y-auto whitespace-pre-wrap text-sm text-gray-800">
              {editingSubmission?.submission_text || 'No text was submitted.'}
            </div>
            {editingSubmission?.submission_file && (
              <button
                type="button"
                onClick={() => handleDownload(editingSubmission)}
                className="mt-2 btn btn-secondary flex items-center space-x-2 text-sm"
              >
                <Download size={16} />
                <span>Download attached file</span>
              </button>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Marks Obtained{currentAssignment ? ` (out of ${marksText(currentAssignment.total_marks)})` : ''}
            </label>
            {/* Marks can't be below 0 or above the assignment's total (the server checks this too) */}
            <input
              type="number"
              required
              value={formData.marks_obtained}
              onChange={(e) => setFormData({ ...formData, marks_obtained: parseFloat(e.target.value) })}
              className="input"
              min="0"
              max={currentAssignment ? Number(currentAssignment.total_marks) : undefined}
              step="any"
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

