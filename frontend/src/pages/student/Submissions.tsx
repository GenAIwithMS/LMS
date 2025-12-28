import React, { useState, useEffect } from 'react';
import { Plus, Search, FileText, Upload } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { getSubmissionsByStudent, submitAssignment, getAssignments } from '../../services/api';
import type { Submission, Assignment } from '../../types';
import toast from 'react-hot-toast';
import { useSearchParams } from 'react-router-dom';

const StudentSubmissions: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<number | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    submission_text: '',
    submission_file: null as File | null,
  });

  useEffect(() => {
    const assignmentId = searchParams.get('assignmentId');
    if (assignmentId) {
      setSelectedAssignmentId(parseInt(assignmentId));
    }
    fetchSubmissions();
    fetchAssignments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      console.log('Fetching submissions...');
      const response = await getSubmissionsByStudent();
      console.log('Submissions API response:', response);
      
      // Handle different response formats
      let submissionsData: Submission[] = [];
      
      if (Array.isArray(response)) {
        submissionsData = response;
        console.log('Response is direct array');
      } else if (response && typeof response === 'object') {
        if (Array.isArray(response.data)) {
          submissionsData = response.data;
          console.log('Response has data array');
        } else if (Array.isArray(response.submissions)) {
          submissionsData = response.submissions;
          console.log('Response has submissions array');
        } else {
          // Try to find any array in the response
          const submissionsArray = Object.values(response).find((val) => Array.isArray(val)) as Submission[] | undefined;
          if (submissionsArray) {
            submissionsData = submissionsArray;
            console.log('Found array in response values');
          } else {
            console.log('No array found in response, response keys:', Object.keys(response));
          }
        }
      }
      
      console.log('Raw submissions data:', submissionsData);
      
      // Map submissions to ensure proper format
      submissionsData = submissionsData.map((submission: any) => ({
        id: submission.id || 0,
        assignment: submission.assignment || submission.assignment_id || '',
        submission_text: submission.submission_text || '',
        submitted_at: submission.submitted_at || '',
        marks_obtained: submission.marks_obtained !== undefined && submission.marks_obtained !== null 
          ? submission.marks_obtained 
          : (submission.marks !== undefined && submission.marks !== null ? submission.marks : undefined),
        feedback: submission.feedback || '',
      }));
      
      console.log('Processed submissions:', submissionsData);
      setSubmissions(submissionsData);
    } catch (error: any) {
      console.error('Error fetching submissions:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        code: error.code,
        config: error.config
      });
      
      let errorMessage = 'Failed to fetch submissions';
      if (error.message?.includes('Network Error') || error.code === 'ECONNREFUSED') {
        errorMessage = 'Cannot connect to server. Please make sure the backend is running on http://localhost:5000';
      } else if (error.response) {
        errorMessage = error.response.data?.message || `Error: ${error.response.status} ${error.response.statusText}`;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
      setSubmissions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssignments = async () => {
    try {
      const data = await getAssignments();
      console.log('Assignments response:', data);
      
      // Handle different response formats
      let assignmentsData: Assignment[] = [];
      
      if (Array.isArray(data)) {
        assignmentsData = data;
      } else if (data && typeof data === 'object') {
        if (Array.isArray(data.assignments)) {
          assignmentsData = data.assignments;
        } else if (data.assignment) {
          assignmentsData = Array.isArray(data.assignment) ? data.assignment : [data.assignment];
        } else {
          // Try to find any array in the response
          const assignmentsArray = Object.values(data).find((val) => Array.isArray(val)) as Assignment[] | undefined;
          if (assignmentsArray) {
            assignmentsData = assignmentsArray;
          }
        }
      }
      
      // Map assignments to ensure proper format
      assignmentsData = assignmentsData.map((assignment: any) => ({
        id: assignment.id || 0,
        title: assignment.title || '',
        description: assignment.description || '',
        due_date: assignment.due_date || assignment.dueDate || '',
        subject: assignment.subject || assignment.subject_name || '',
        total_marks: assignment.total_marks || assignment.totalMarks || 100,
      }));
      
      setAssignments(assignmentsData);
    } catch (error) {
      console.error('Failed to fetch assignments:', error);
      setAssignments([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssignmentId) {
      toast.error('Please select an assignment');
      return;
    }

    // Validate that at least submission text or file is provided
    if (!formData.submission_text && !formData.submission_file) {
      toast.error('Please provide either submission text or upload a file');
      return;
    }

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('assignment_id', selectedAssignmentId.toString());
      
      if (formData.submission_text && formData.submission_text.trim()) {
        formDataToSend.append('submission_text', formData.submission_text);
      }
      
      if (formData.submission_file) {
        formDataToSend.append('submission_file', formData.submission_file);
      }

      console.log('Submitting assignment:', {
        assignment_id: selectedAssignmentId,
        has_text: !!formData.submission_text,
        has_file: !!formData.submission_file
      });

      const response = await submitAssignment(formDataToSend);
      console.log('Submission response:', response);
      
      toast.success(response.message || 'Assignment submitted successfully');
      setIsModalOpen(false);
      resetForm();
      fetchSubmissions();
    } catch (error: any) {
      console.error('Submission error:', error);
      console.error('Error response:', error.response);
      const errorMessage = error.response?.data?.message 
        || error.response?.data?.error 
        || error.message 
        || 'Submission failed. Please try again.';
      toast.error(errorMessage);
    }
  };

  const resetForm = () => {
    setFormData({ submission_text: '', submission_file: null });
    setSelectedAssignmentId(null);
  };

  const filteredSubmissions = submissions.filter((submission) =>
    submission.assignment?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
          <h1 className="text-3xl font-bold text-gray-900">My Submissions</h1>
          <p className="text-gray-600 mt-2">View and submit your assignments</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setIsModalOpen(true);
          }}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Submit Assignment</span>
        </button>
      </div>

      <div className="card mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search submissions..."
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
              <th>Assignment</th>
              <th>Submission Text</th>
              <th>Submitted At</th>
              <th>Marks</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody>
            {filteredSubmissions.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-500">
                  No submissions found
                </td>
              </tr>
            ) : (
              filteredSubmissions.map((submission) => (
                <tr key={submission.id}>
                  <td>{submission.id}</td>
                  <td>{submission.assignment}</td>
                  <td className="max-w-xs truncate">{submission.submission_text || 'N/A'}</td>
                  <td>{submission.submitted_at ? new Date(submission.submitted_at).toLocaleDateString() : 'N/A'}</td>
                  <td>{submission.marks_obtained !== undefined ? submission.marks_obtained : 'Not graded'}</td>
                  <td className="max-w-xs truncate">{submission.feedback || 'N/A'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
        title="Submit Assignment"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Assignment</label>
            <select
              required
              value={selectedAssignmentId || ''}
              onChange={(e) => setSelectedAssignmentId(e.target.value ? parseInt(e.target.value) : null)}
              className="input"
            >
              <option value="">Select an assignment</option>
              {assignments.map((assignment) => (
                <option key={assignment.id} value={assignment.id}>
                  {assignment.title}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Submission Text</label>
            <textarea
              value={formData.submission_text}
              onChange={(e) => setFormData({ ...formData, submission_text: e.target.value })}
              className="input"
              rows={5}
              placeholder="Enter your submission text here..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload File</label>
            <div className="flex items-center space-x-2">
              <label className="flex-1 cursor-pointer">
                <input
                  type="file"
                  onChange={(e) => setFormData({ ...formData, submission_file: e.target.files?.[0] || null })}
                  className="hidden"
                />
                <div className="input flex items-center space-x-2">
                  <Upload size={20} className="text-gray-400" />
                  <span className="text-gray-500">
                    {formData.submission_file ? formData.submission_file.name : 'Choose a file'}
                  </span>
                </div>
              </label>
            </div>
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
              Submit Assignment
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default StudentSubmissions;

