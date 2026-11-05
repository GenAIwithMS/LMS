import React, { useState, useEffect } from 'react';
import { Search, FileText, Calendar, Upload, Send, Lock, AlertCircle } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { getAssignments, submitAssignment, getSubmissionsByStudent } from '../../services/api';
import type { Assignment } from '../../types';
import toast from 'react-hot-toast';
import { showError, showSuccess } from '../../utils/errorHandler';

// One submission of this student, as the server sends it
interface MySubmission {
  id: number;
  assignment_id: number;
  assignment: string;
  submission_text: string | null;
  submission_file: string | null;
  submitted_at: string | null;
  marks: string | null;
  feedback: string | null;
}

// The file types the server accepts, and the size limit
const ACCEPTED_FILES = '.pdf,.doc,.docx,.txt,.ppt,.pptx,.xls,.xlsx,.zip,.png,.jpg,.jpeg';
const MAX_FILE_SIZE = 10 * 1024 * 1024;

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Today as "YYYY-MM-DD" in the student's own time zone
const todayText = (): string => {
  return new Date().toLocaleDateString('en-CA');
};

// "2026-11-12" -> "12 Nov 2026". Read from the text itself, so time zones can't move it a day.
const dateText = (value: string | null | undefined): string => {
  if (!value) {
    return '-';
  }
  const parts = value.slice(0, 10).split('-');
  if (parts.length !== 3) {
    return value;
  }
  const year = parts[0];
  const month = MONTHS[parseInt(parts[1], 10) - 1];
  const day = parseInt(parts[2], 10);
  if (!month || isNaN(day)) {
    return value;
  }
  return `${day} ${month} ${year}`;
};

// Marks without needless decimals: "10" instead of "10.00", but "7.5" stays
const marksText = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  const number = Number(value);
  if (isNaN(number)) {
    return String(value);
  }
  return String(number);
};

const StudentAssignments: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [submissions, setSubmissions] = useState<MySubmission[]>([]);
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

      // The server sends {"data": [...]}; other shapes are kept just in case
      let submissionsData: MySubmission[] = [];
      if (Array.isArray(data)) {
        submissionsData = data;
      } else if (data && Array.isArray(data.data)) {
        submissionsData = data.data;
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

  // Overdue only after the due date: on the due day itself work can still be handed in
  const isOverdue = (dueDate: string): boolean => {
    if (!dueDate) {
      return false;
    }
    return dueDate.slice(0, 10) < todayText();
  };

  const isDueToday = (dueDate: string): boolean => {
    if (!dueDate) {
      return false;
    }
    return dueDate.slice(0, 10) === todayText();
  };

  // This student's submission for an assignment, or null
  const findSubmission = (assignmentId: number): MySubmission | null => {
    for (const submission of submissions) {
      if (submission.assignment_id === assignmentId) {
        return submission;
      }
    }
    return null;
  };

  // A submission is graded once the teacher has given marks or feedback
  const isGraded = (submission: MySubmission | null): boolean => {
    if (!submission) {
      return false;
    }
    const hasMarks = submission.marks !== null && submission.marks !== undefined && submission.marks !== '';
    const hasFeedback = !!submission.feedback;
    return hasMarks || hasFeedback;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssignment) return;

    // No submissions after the due date
    if (isOverdue(selectedAssignment.due_date)) {
      toast.error('The due date has passed, so this assignment can no longer be submitted');
      return;
    }

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('assignment_id', selectedAssignment.id.toString());
      if (formData.submission_text) {
        formDataToSend.append('submission_text', formData.submission_text);
      }
      if (formData.submission_file) {
        formDataToSend.append('submission_file', formData.submission_file);
      }

      const response = await submitAssignment(formDataToSend);
      showSuccess(response?.message || 'Assignment submitted');
      setIsModalOpen(false);
      resetForm();
      fetchSubmissions();
    } catch (error: any) {
      showError(error, 'Submission failed');
    }
  };

  const resetForm = () => {
    setFormData({ submission_text: '', submission_file: null });
    setSelectedAssignment(null);
  };

  const openSubmitModal = (assignment: Assignment) => {
    if (isOverdue(assignment.due_date)) {
      toast.error('The due date has passed, so this assignment can no longer be submitted');
      return;
    }
    // When updating, start from the earlier text
    const earlier = findSubmission(assignment.id);
    let earlierText = '';
    if (earlier && earlier.submission_text) {
      earlierText = earlier.submission_text;
    }
    setFormData({ submission_text: earlierText, submission_file: null });
    setSelectedAssignment(assignment);
    setIsModalOpen(true);
  };

  // A chosen file must be one of the accepted types and not larger than 10 MB
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file && file.size > MAX_FILE_SIZE) {
      toast.error('The file is larger than 10 MB');
      e.target.value = '';
      setFormData({ ...formData, submission_file: null });
      return;
    }
    setFormData({ ...formData, submission_file: file });
  };

  const filteredAssignments = assignments.filter((assignment) => {
    const title = assignment?.title || '';
    const subject = assignment?.subject || '';
    const search = searchTerm.toLowerCase();
    return title.toLowerCase().includes(search) || subject.toLowerCase().includes(search);
  });

  // Work still to come first (soonest due first), then the closed ones (most recent first)
  const sortedAssignments = [...filteredAssignments].sort((a, b) => {
    const aClosed = isOverdue(a.due_date);
    const bClosed = isOverdue(b.due_date);
    if (aClosed !== bClosed) {
      return aClosed ? 1 : -1;
    }
    if (aClosed) {
      return b.due_date.localeCompare(a.due_date);
    }
    return a.due_date.localeCompare(b.due_date);
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const selectedSubmission = selectedAssignment ? findSubmission(selectedAssignment.id) : null;

  return (
    <div>
      {/* On a phone the title and the search box stack, so nothing is pushed off the screen */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-2">View and submit your assignments</p>
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Search Bar */}
          <div className="relative w-full sm:w-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 pr-10 py-2 text-sm w-full sm:w-[250px] transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedAssignments.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No assignments found</div>
        ) : (
          sortedAssignments.map((assignment) => {
            const submission = findSubmission(assignment.id);
            const submitted = submission !== null;
            const graded = isGraded(submission);
            const overdue = isOverdue(assignment.due_date);
            const dueToday = isDueToday(assignment.due_date);

            let dueClass = 'text-gray-500';
            if (overdue && !submitted) {
              dueClass = 'text-red-600 font-medium';
            } else if (dueToday) {
              dueClass = 'text-amber-600 font-medium';
            }

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
                    <span className={dueClass}>
                      Due: {dateText(assignment.due_date)}
                    </span>
                  </div>
                  <span className="font-medium text-gray-900">{marksText(assignment.total_marks)} marks</span>
                </div>

                {/* The status of this student's work */}
                {graded && submission ? (
                  <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm">
                    <p className="font-semibold text-green-800">
                      Marks: {marksText(submission.marks)} / {marksText(assignment.total_marks)}
                    </p>
                    {submission.feedback && (
                      <p className="text-gray-700 mt-1">
                        <span className="font-medium">Teacher's feedback:</span> {submission.feedback}
                      </p>
                    )}
                  </div>
                ) : submitted && submission ? (
                  <>
                    <div className="mb-3 text-xs text-green-700 font-medium">
                      ✓ Submitted on {dateText(submission.submitted_at)}
                    </div>
                    {overdue ? (
                      <div className="text-xs text-gray-500">Waiting for the teacher to check it</div>
                    ) : (
                      <button
                        onClick={() => openSubmitModal(assignment)}
                        className="w-full btn btn-secondary flex items-center justify-center space-x-2"
                      >
                        <Upload size={18} />
                        <span>Update submission</span>
                      </button>
                    )}
                  </>
                ) : overdue ? (
                  <>
                    <div className="mb-3 text-xs text-red-600 font-medium">Not submitted</div>
                    <button
                      disabled
                      className="w-full btn flex items-center justify-center space-x-2 bg-gray-200 text-gray-500 cursor-not-allowed opacity-60"
                    >
                      <Lock size={18} />
                      <span>Submission Closed</span>
                    </button>
                  </>
                ) : (
                  <>
                    {dueToday && (
                      <div className="mb-3 text-xs text-amber-600 font-medium">Due today</div>
                    )}
                    <button
                      onClick={() => openSubmitModal(assignment)}
                      className="w-full btn btn-primary flex items-center justify-center space-x-2"
                    >
                      <Upload size={18} />
                      <span>Submit</span>
                    </button>
                  </>
                )}
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
          ? `${selectedSubmission ? 'Update submission' : 'Submit'}: ${selectedAssignment.title}`
          : 'Submit Assignment'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {selectedSubmission && (
            <p className="text-sm text-amber-700 bg-amber-50 p-3 rounded-lg">
              This replaces your earlier submission.
            </p>
          )}
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
                  accept={ACCEPTED_FILES}
                  onChange={handleFileChange}
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
            <p className="text-xs text-gray-500 mt-1">PDF, Word, PowerPoint, Excel, text, zip or image; up to 10 MB</p>
            {selectedSubmission && selectedSubmission.submission_file && (
              <p className="text-xs text-gray-600 mt-1">Your earlier file stays unless you choose a new one.</p>
            )}
          </div>
          {selectedAssignment && (
            <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              <p><strong>Due Date:</strong> {dateText(selectedAssignment.due_date)}</p>
              <p><strong>Total marks:</strong> {marksText(selectedAssignment.total_marks)}</p>
              {isOverdue(selectedAssignment.due_date) && (
                <div className="flex items-center space-x-2 text-red-600 font-medium mt-2">
                  <AlertCircle size={16} />
                  <span>The due date has passed, so this assignment can no longer be submitted</span>
                </div>
              )}
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
            <button
              type="submit"
              disabled={selectedAssignment ? isOverdue(selectedAssignment.due_date) : false}
              className={`btn btn-primary flex items-center space-x-2 ${
                selectedAssignment && isOverdue(selectedAssignment.due_date)
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-60'
                  : ''
              }`}
            >
              <Send size={18} />
              <span>{selectedSubmission ? 'Update' : 'Submit'}</span>
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default StudentAssignments;
