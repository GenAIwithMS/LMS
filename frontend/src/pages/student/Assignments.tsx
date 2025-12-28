import React, { useState, useEffect } from 'react';
import { Search, FileText, Calendar, Upload, Send } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { getAssignments, submitAssignment, getSubmissionsByStudent } from '../../services/api';
import type { Assignment, Submission } from '../../types';
import toast from 'react-hot-toast';

const StudentAssignments: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);
  const [formData, setFormData] = useState({
    submission_text: '',
    submission_file: null as File | null,
  });

  useEffect(() => {
    fetchAssignments();
    fetchSubmissions();
  }, []);

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const data = await getAssignments();
      
      // Handle different response formats
      let assignmentsData: Assignment[] = [];
      
      if (Array.isArray(data)) {
        assignmentsData = data;
      } else if (data && Array.isArray(data.assignments)) {
        assignmentsData = data.assignments;
      } else if (data && data.assignment) {
        assignmentsData = Array.isArray(data.assignment) ? data.assignment : [data.assignment];
      } else if (data && typeof data === 'object') {
        const assignmentsArray = Object.values(data).find((val) => Array.isArray(val)) as Assignment[] | undefined;
        if (assignmentsArray) {
          assignmentsData = assignmentsArray;
        }
      }
      
      // Normalize assignment data
      assignmentsData = assignmentsData.map((assignment: any) => ({
        id: assignment.id || 0,
        title: assignment.title || '',
        description: assignment.description || '',
        due_date: assignment.due_date || assignment.dueDate || '',
        subject: assignment.subject || assignment.subject_name || '',
        teacher: assignment.teacher || assignment.teacher_name || '',
        total_marks: assignment.total_marks || assignment.totalMarks || 100,
      }));
      
      setAssignments(assignmentsData);
    } catch (error) {
      toast.error('Failed to fetch assignments');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubmissions = async () => {
    try {
      const data = await getSubmissionsByStudent();
      
      // Handle different response formats
      let submissionsData: Submission[] = [];
      
      if (Array.isArray(data)) {
        submissionsData = data;
      } else if (data && Array.isArray(data.submissions)) {
        submissionsData = data.submissions;
      } else if (data && data.submission) {
        submissionsData = Array.isArray(data.submission) ? data.submission : [data.submission];
      }
      
      setSubmissions(submissionsData);
    } catch (error) {
      console.error('Failed to fetch submissions');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssignment) return;

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('assignment_id', selectedAssignment.id.toString());
      if (formData.submission_text) {
        formDataToSend.append('submission_text', formData.submission_text);
      }
      if (formData.submission_file) {
        formDataToSend.append('submission_file', formData.submission_file);
      }

      await submitAssignment(formDataToSend);
      toast.success('Assignment submitted successfully');
      setIsModalOpen(false);
      resetForm();
      fetchSubmissions();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Submission failed');
    }
  };

  const resetForm = () => {
    setFormData({ submission_text: '', submission_file: null });
    setSelectedAssignment(null);
  };

  const openSubmitModal = (assignment: Assignment) => {
    setSelectedAssignment(assignment);
    setIsModalOpen(true);
  };

  const hasSubmission = (assignmentId: number) => {
    // Check if there's a submission for this assignment
    const assignment = assignments.find(a => a.id === assignmentId);
    if (!assignment) return false;
    
    return submissions.some((sub) => {
      // Try to match by assignment ID if available, or by assignment name/title
      const subAssignmentId = (sub as any).assignment_id;
      const subAssignmentName = sub.assignment;
      
      return subAssignmentId === assignmentId || 
             (assignment && subAssignmentName && assignment.title && 
              subAssignmentName.toLowerCase().includes(assignment.title.toLowerCase()));
    });
  };

  const filteredAssignments = assignments.filter((assignment) => {
    const title = assignment?.title || '';
    const subject = assignment?.subject || '';
    const search = searchTerm.toLowerCase();
    return title.toLowerCase().includes(search) || subject.toLowerCase().includes(search);
  });

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date();
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
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-2">View and submit your assignments</p>
        </div>
      </div>

      <div className="card mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search assignments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAssignments.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No assignments found</div>
        ) : (
          filteredAssignments.map((assignment) => {
            const submitted = hasSubmission(assignment.id);
            return (
              <div key={assignment.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{assignment.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{assignment.subject}</p>
                  </div>
                  <FileText className="text-primary-600" size={24} />
                </div>
                <p className="text-gray-600 mb-4 line-clamp-2">{assignment.description}</p>
                <div className="flex items-center justify-between text-sm mb-4">
                  <div className="flex items-center space-x-2 text-gray-500">
                    <Calendar size={16} />
                    <span className={isOverdue(assignment.due_date) ? 'text-red-600 font-medium' : ''}>
                      Due: {assignment.due_date}
                    </span>
                  </div>
                  <span className="font-medium text-gray-900">{assignment.total_marks} marks</span>
                </div>
                {isOverdue(assignment.due_date) && (
                  <div className="mb-3 text-xs text-red-600 font-medium">Overdue</div>
                )}
                <button
                  onClick={() => openSubmitModal(assignment)}
                  className={`w-full btn flex items-center justify-center space-x-2 ${
                    submitted 
                      ? 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200' 
                      : 'btn-primary'
                  }`}
                >
                  {submitted ? (
                    <>
                      <span>✓</span>
                      <span>Submitted</span>
                    </>
                  ) : (
                    <>
                      <Upload size={18} />
                      <span>Submit</span>
                    </>
                  )}
                </button>
              </div>
            );
          })
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
        title={selectedAssignment 
          ? `${hasSubmission(selectedAssignment.id) ? 'Resubmit' : 'Submit'}: ${selectedAssignment.title}` 
          : 'Submit Assignment'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
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
                <div className="input flex items-center space-x-2 cursor-pointer hover:bg-gray-50">
                  <Upload size={20} className="text-gray-400" />
                  <span className="text-gray-500">
                    {formData.submission_file ? formData.submission_file.name : 'Choose a file (optional)'}
                  </span>
                </div>
              </label>
            </div>
          </div>
          {selectedAssignment && (
            <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              <p><strong>Due Date:</strong> {selectedAssignment.due_date}</p>
              <p><strong>Total Marks:</strong> {selectedAssignment.total_marks}</p>
            </div>
          )}
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
            <button type="submit" className="btn btn-primary flex items-center space-x-2">
              <Send size={18} />
              <span>Submit</span>
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default StudentAssignments;

