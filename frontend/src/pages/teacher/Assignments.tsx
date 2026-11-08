import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Eye, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getAssignments, createAssignment, updateAssignment, deleteAssignment, getMyClasses } from '../../services/api';
import type { Assignment, TeachingItem } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import { useNavigate, useSearchParams } from 'react-router-dom';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// The due date as "2025-01-01", for the date box. The server may send "2025-01-01" or
// "Wed, 01 Jan 2025 00:00:00 GMT". The date is read from the text itself, so it can't
// move a day because of the time zone.
const dateBoxValue = (text: string): string => {
  if (!text) {
    return '';
  }
  if (/^\d{4}-\d{2}-\d{2}/.test(text)) {
    return text.slice(0, 10);
  }
  const match = text.match(/(\d{1,2}) ([A-Za-z]{3}) (\d{4})/);
  if (!match) {
    return '';
  }
  const monthIndex = MONTHS.indexOf(match[2]);
  if (monthIndex === -1) {
    return '';
  }
  const month = String(monthIndex + 1).padStart(2, '0');
  const day = match[1].padStart(2, '0');
  return `${match[3]}-${month}-${day}`;
};

// The due date in words, like "1 Jan 2025"
const readableDate = (text: string): string => {
  const value = dateBoxValue(text);
  if (!value) {
    return text || '-';
  }
  const year = value.slice(0, 4);
  const monthIndex = parseInt(value.slice(5, 7)) - 1;
  const day = parseInt(value.slice(8, 10));
  return `${day} ${MONTHS[monthIndex]} ${year}`;
};

// Marks without needless decimals: "10" instead of "10.00", but "7.5" stays
const marksText = (value: number | string): string => {
  const number = Number(value);
  if (isNaN(number)) {
    return String(value);
  }
  return String(number);
};

// Today as "2026-11-05", in the user's own time zone
const todayText = (): string => {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
};

// An assignment as shown on this page: it also knows which section it is for
interface SectionAssignment extends Assignment {
  section_id: number | null;
  section_name: string | null;
  topic_title?: string | null;
}

// The syllabus topic a new assignment is set on (when it comes from a done topic)
interface FromTopic {
  id: number;
  title: string;
}

const TeacherAssignments: React.FC = () => {
  const [assignments, setAssignments] = useState<SectionAssignment[]>([]);
  // What the teacher teaches: one item per section and subject, like "Class 5 - A · Maths"
  const [teaching, setTeaching] = useState<TeachingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<SectionAssignment | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingAssignment, setDeletingAssignment] = useState<SectionAssignment | null>(null);
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
    subject_id: '',
    subject_name: '',
    section_id: '',
    total_marks: 100,
  });
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [fromTopic, setFromTopic] = useState<FromTopic | null>(null);

  useEffect(() => {
    fetchAssignments();
    fetchTeaching();
  }, []);

  // Sent here from a done topic in the syllabus (?new=1&section=..&subject=..&topic=..&topicTitle=..):
  // open Create Assignment with the class, subject and topic filled in
  useEffect(() => {
    if (searchParams.get('new') !== '1' || teaching.length === 0) {
      return;
    }
    const sectionId = searchParams.get('section') || '';
    const subjectId = searchParams.get('subject') || '';
    const topicId = Number(searchParams.get('topic'));
    const topicTitle = searchParams.get('topicTitle') || '';

    let subjectName = '';
    for (const item of teaching) {
      if (String(item.section_id) === sectionId && String(item.subject_id) === subjectId) {
        subjectName = item.subject_name;
      }
    }
    setEditingAssignment(null);
    setFormData({ title: topicTitle, description: '', due_date: '', subject_id: subjectId, subject_name: subjectName, section_id: sectionId, total_marks: 100 });
    if (topicId) {
      setFromTopic({ id: topicId, title: topicTitle });
    }
    setIsModalOpen(true);
    // So a reload doesn't open it again
    setSearchParams({}, { replace: true });
  }, [teaching, searchParams]);

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

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchAssignments = async () => {
    try {
      const data = await getAssignments();
      
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
      
      // Ensure all assignments have required fields with defaults
      assignmentsData = assignmentsData.map((assignment: any) => ({
        id: assignment.id || 0,
        title: assignment.title || '',
        description: assignment.description || '',
        due_date: assignment.due_date || assignment.dueDate || '',
        subject: assignment.subject || assignment.subject_name || '',
        subject_id: assignment.subject_id,
        section_id: assignment.section_id || null,
        section_name: assignment.section_name || null,
        teacher: assignment.teacher || assignment.teacher_name || '',
        total_marks: assignment.total_marks || assignment.totalMarks || 100,
        topic_title: assignment.topic_title || null,
      }));
      
      setAssignments(assignmentsData);
    } catch (error: any) {
      console.error('Error fetching assignments:', error);
      showError(error, 'Failed to fetch assignments');
      setAssignments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTeaching = async () => {
    try {
      const data = await getMyClasses();
      if (data && Array.isArray(data.teaching)) {
        setTeaching(data.teaching);
      } else {
        setTeaching([]);
      }
    } catch (error: any) {
      showError(error, 'Failed to load the subjects you teach');
      setTeaching([]);
    }
  };

  // The class picker's value is "sectionId-subjectId", like "3-12"
  const teachingKey = (sectionId: number | string, subjectId: number | string) => {
    return `${sectionId}-${subjectId}`;
  };

  // Keep the chosen section, subject ID and subject name together
  const handleTeachingChange = (key: string) => {
    let sectionId = '';
    let subjectId = '';
    let subjectName = '';
    for (const item of teaching) {
      if (teachingKey(item.section_id, item.subject_id) === key) {
        sectionId = String(item.section_id);
        subjectId = String(item.subject_id);
        subjectName = item.subject_name;
      }
    }
    setFormData({ ...formData, section_id: sectionId, subject_id: subjectId, subject_name: subjectName });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Send the IDs: names can repeat, IDs can't
    const submitData = {
      title: formData.title,
      description: formData.description,
      due_date: formData.due_date,
      subject_name: formData.subject_name,
      total_marks: formData.total_marks,
      subject_id: formData.subject_id ? Number(formData.subject_id) : undefined,
      section_id: formData.section_id ? Number(formData.section_id) : undefined,
      topic_id: fromTopic ? fromTopic.id : undefined,
    };
    try {
      if (editingAssignment) {
        // The section of an assignment doesn't change after it is set
        const updateData = {
          title: submitData.title,
          description: submitData.description,
          due_date: submitData.due_date,
          total_marks: submitData.total_marks,
          subject_id: submitData.subject_id,
        };
        await updateAssignment(editingAssignment.id, updateData);
        showSuccess('Assignment updated successfully');
      } else {
        await createAssignment(submitData);
        showSuccess('Assignment created successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchAssignments();
    } catch (error: any) {
      showError(error, 'Failed to save assignment');
    }
  };

  const handleEdit = (assignment: SectionAssignment) => {
    setEditingAssignment(assignment);
    setFormData({
      title: assignment.title,
      description: assignment.description,
      due_date: dateBoxValue(assignment.due_date),
      subject_id: assignment.subject_id ? String(assignment.subject_id) : '',
      subject_name: assignment.subject,
      section_id: assignment.section_id ? String(assignment.section_id) : '',
      total_marks: Number(assignment.total_marks),
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (assignment: SectionAssignment) => {
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
    setFormData({ title: '', description: '', due_date: '', subject_id: '', subject_name: '', section_id: '', total_marks: 100 });
    setEditingAssignment(null);
    setFromTopic(null);
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

  // Each subject name once, for the filter
  const subjectNames: string[] = [];
  for (const item of teaching) {
    if (!subjectNames.includes(item.subject_name)) {
      subjectNames.push(item.subject_name);
    }
  }

  // A new assignment can't be due in the past. When editing, an old due date can stay
  // as it is; only a changed date has to be today or later.
  let dueDateMin: string | undefined = todayText();
  if (editingAssignment && formData.due_date === dateBoxValue(editingAssignment.due_date)) {
    dueDateMin = undefined;
  }

  // On the edit form, the picker shows the assignment's own section and subject
  let pickerKey = '';
  if (formData.section_id && formData.subject_id) {
    pickerKey = teachingKey(formData.section_id, formData.subject_id);
  }

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
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-2">Create and manage assignments</p>
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
                      {subjectNames.map((name) => (
                        <option key={name} value={name}>
                          {name}
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
                  <p className="text-sm text-gray-500 mt-1">
                    {assignment.section_name ? `${assignment.section_name} · ${assignment.subject}` : assignment.subject}
                  </p>
                  {assignment.topic_title && (
                    <p className="text-xs text-primary-700 mt-1">Topic: {assignment.topic_title}</p>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <button onClick={() => navigate(`/teacher/submissions?assignmentId=${assignment.id}`)} className="p-2 text-green-600 hover:bg-green-50 rounded" title="View Submissions" aria-label={`View submissions for ${assignment.title}`}>
                    <Eye size={18} />
                  </button>
                  <button onClick={() => handleEdit(assignment)} className="p-2 text-blue-600 hover:bg-blue-50 rounded" title={`Edit ${assignment.title}`} aria-label={`Edit ${assignment.title}`}>
                    <Edit size={18} />
                  </button>
                  <button onClick={() => handleDeleteClick(assignment)} className="p-2 text-red-600 hover:bg-red-50 rounded" title={`Delete ${assignment.title}`} aria-label={`Delete ${assignment.title}`}>
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              <p className="text-gray-600 mb-4 line-clamp-2">{assignment.description}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Due: {readableDate(assignment.due_date)}</span>
                <span className="font-medium text-gray-900">{marksText(assignment.total_marks)} marks</span>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingAssignment ? 'Edit Assignment' : 'Create Assignment'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {fromTopic && !editingAssignment && (
            <p className="text-sm text-primary-700 bg-primary-50 rounded-lg px-3 py-2">On topic: {fromTopic.title}</p>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea required value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="input" rows={4} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Class and Subject</label>
            <select required value={pickerKey} onChange={(e) => handleTeachingChange(e.target.value)} className="input" disabled={editingAssignment !== null && editingAssignment.section_id !== null}>
              <option value="">Select a class and subject</option>
              {teaching.map((item) => (
                <option key={teachingKey(item.section_id, item.subject_id)} value={teachingKey(item.section_id, item.subject_id)}>
                  {item.section_name} · {item.subject_name}
                </option>
              ))}
            </select>
            {teaching.length === 0 && (
              <p className="text-xs text-red-600 mt-1">The admin hasn't given you any subjects yet.</p>
            )}
            {editingAssignment !== null && editingAssignment.section_id !== null && (
              <p className="text-xs text-gray-500 mt-1">The class of an assignment can't be changed.</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
              <input type="date" required min={dueDateMin} value={formData.due_date} onChange={(e) => setFormData({ ...formData, due_date: e.target.value })} className="input" />
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

