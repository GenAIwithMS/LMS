import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import {
  getStudents,
  addStudent,
  updateStudent,
  deleteStudent,
  getStudentDeleteCheck,
  getSections,
} from '../../services/api';
import type { Student, Section } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';

const AdminStudents: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterSection, setFilterSection] = useState<string>('all');
  const [showOptions, setShowOptions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingStudent, setDeletingStudent] = useState<Student | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  // What the student still has (marks, attendance...), loaded when the delete window opens
  const [deleteRecords, setDeleteRecords] = useState<{ label: string; count: number }[] | null>(null);
  const optionsRef = useRef<HTMLDivElement>(null);
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
    section_id: '',
    section_name: '',
    roll_number: '',
    admission_number: '',
    guardian_name: '',
    guardian_phone: '',
    date_of_birth: '',
  });

  useEffect(() => {
    fetchStudents();
    fetchSections();
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

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const data = await getStudents();
      
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
      
      // Ensure all students have required fields with proper section mapping
      studentsData = studentsData.map((student: any) => ({
        id: student.id || 0,
        name: student.name || '',
        username: student.username || '',
        email: student.email || '',
        section: student.section_full_name || student.section || student.section_name || '',
        section_id: student.section_id,
        roll_number: student.roll_number,
        admission_number: student.admission_number,
        guardian_name: student.guardian_name,
        guardian_phone: student.guardian_phone,
        date_of_birth: student.date_of_birth,
      }));
      
      setStudents(studentsData);
    } catch (error: any) {
      console.error('Error fetching students:', error);
      showError(error, 'Failed to fetch students');
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSections = async () => {
    try {
      const data = await getSections();
      setSections(Array.isArray(data) ? data : data.section ? [data.section] : []);
    } catch (error) {
      console.error('Failed to fetch sections');
    }
  };

  // Keep the chosen section's ID and name together
  const handleSectionChange = (sectionId: string) => {
    let sectionName = '';
    for (const section of sections) {
      if (String(section.id) === sectionId) {
        sectionName = section.name;
      }
    }
    setFormData({ ...formData, section_id: sectionId, section_name: sectionName });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Send the ID: names can repeat, IDs can't
    const submitData: any = { ...formData, section_id: formData.section_id ? Number(formData.section_id) : undefined };
    // Leave out empty optional fields (an empty date or admission number is not a value)
    for (const key of ['roll_number', 'admission_number', 'guardian_name', 'guardian_phone', 'date_of_birth', 'password']) {
      if (!submitData[key]) {
        delete submitData[key];
      }
    }
    try {
      if (editingStudent) {
        await updateStudent(editingStudent.id, submitData);
        showSuccess('Student updated successfully');
      } else {
        await addStudent(submitData);
        showSuccess('Student added successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchStudents();
    } catch (error: any) {
      showError(error, 'Failed to save student');
    }
  };

  const handleEdit = (student: Student) => {
    setEditingStudent(student);
    setFormData({
      name: student.name || '',
      username: student.username || '',
      email: student.email || '',
      password: '',
      section_id: student.section_id ? String(student.section_id) : '',
      section_name: student.section || '',
      roll_number: student.roll_number || '',
      admission_number: student.admission_number || '',
      guardian_name: student.guardian_name || '',
      guardian_phone: student.guardian_phone || '',
      date_of_birth: student.date_of_birth || '',
    });
    setIsModalOpen(true);
  };

  // Open the delete window and load what the student still has
  const handleDeleteClick = async (student: Student) => {
    setDeletingStudent(student);
    setDeleteRecords(null);
    setShowDeleteConfirm(true);
    try {
      const data = await getStudentDeleteCheck(student.id);
      setDeleteRecords(Array.isArray(data.records) ? data.records : []);
    } catch (error: any) {
      showError(error, 'Failed to check the student\'s records');
      setShowDeleteConfirm(false);
      setDeletingStudent(null);
    }
  };

  const closeDeleteWindow = () => {
    setShowDeleteConfirm(false);
    setDeletingStudent(null);
    setDeleteRecords(null);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingStudent || deleteRecords === null) return;

    // With records, the admin has seen the list and chose to delete them too
    let removeRecords = false;
    if (deleteRecords.length > 0) {
      removeRecords = true;
    }

    setIsDeleting(true);
    try {
      await deleteStudent(deletingStudent.id, removeRecords);
      showSuccess('Student deleted successfully');
      closeDeleteWindow();
      fetchStudents();
    } catch (error: any) {
      showError(error, 'Failed to delete student');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ name: '', username: '', email: '', password: '', section_id: '', section_name: '', roll_number: '', admission_number: '', guardian_name: '', guardian_phone: '', date_of_birth: '' });
    setEditingStudent(null);
  };

  // A roll number as a number, or null when it's empty or not a number
  const rollAsNumber = (roll: string | null | undefined): number | null => {
    if (!roll || roll.trim() === '') return null;
    const value = Number(roll.trim());
    if (isNaN(value)) return null;
    return value;
  };

  // Sort by roll number: numbers in number order, students without a roll number last
  const compareRoll = (a: Student, b: Student): number => {
    const aRoll = a.roll_number || '';
    const bRoll = b.roll_number || '';
    if (aRoll === '' && bRoll === '') return 0;
    if (aRoll === '') return 1;
    if (bRoll === '') return -1;
    const aNumber = rollAsNumber(aRoll);
    const bNumber = rollAsNumber(bRoll);
    let result = 0;
    if (aNumber !== null && bNumber !== null) {
      result = aNumber - bNumber;
    } else {
      result = aRoll.localeCompare(bRoll);
    }
    if (sortOrder === 'desc') {
      result = -result;
    }
    return result;
  };

  const filteredStudents = students
    .filter((student) => {
      // Search the name, email, username, section (e.g. "6 - A") and roll number
      const term = searchTerm.toLowerCase();
      const matchesSearch =
        student.name?.toLowerCase().includes(term) ||
        student.email?.toLowerCase().includes(term) ||
        student.username?.toLowerCase().includes(term) ||
        (student.section || '').toLowerCase().includes(term) ||
        (student.roll_number || '').toLowerCase().includes(term);
      const matchesSection = filterSection === 'all' || student.section === filterSection;
      return matchesSearch && matchesSection;
    })
    .sort((a, b) => {
      if (sortBy === 'roll') {
        return compareRoll(a, b);
      }

      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'name':
          aValue = (a.name || '').toLowerCase();
          bValue = (b.name || '').toLowerCase();
          break;
        case 'email':
          aValue = (a.email || '').toLowerCase();
          bValue = (b.email || '').toLowerCase();
          break;
        case 'username':
          aValue = (a.username || '').toLowerCase();
          bValue = (b.username || '').toLowerCase();
          break;
        case 'section':
          aValue = (a.section || '').toLowerCase();
          bValue = (b.section || '').toLowerCase();
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
          <h1 className="text-3xl font-bold text-gray-900">Students</h1>
          <p className="text-gray-600 mt-2">Manage all students in the system</p>
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
                title="Sort and filter"
                aria-label="Sort and filter"
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
                      <option value="roll">Roll No.</option>
                      <option value="name">Name</option>
                      <option value="email">Email</option>
                      <option value="username">Username</option>
                      <option value="section">Section</option>
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

                  {/* Filter Section */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Section</label>
                    <select
                      value={filterSection}
                      onChange={(e) => setFilterSection(e.target.value)}
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="all">All Sections</option>
                      {sections.map((section) => (
                        <option key={section.id} value={section.full_name || section.name}>
                          {section.full_name || section.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            onClick={() => {
              resetForm();
              setIsModalOpen(true);
            }}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Add Student</span>
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Roll No.</th>
              <th>Name</th>
              <th>Username</th>
              <th>Email</th>
              <th>Section</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-500">
                  No students found
                </td>
              </tr>
            ) : (
              filteredStudents.map((student) => (
                <tr key={student.id}>
                  <td>{student.id}</td>
                  <td>{student.roll_number || '-'}</td>
                  <td>{student.name}</td>
                  <td>{student.username}</td>
                  <td>{student.email}</td>
                  <td>{student.section}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEdit(student)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                        title={`Edit ${student.name}`}
                        aria-label={`Edit ${student.name}`}
                      >
                        <Edit size={18} />
                      </button>
                      <button
                        onClick={() => handleDeleteClick(student)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                        title={`Delete ${student.name}`}
                        aria-label={`Delete ${student.name}`}
                      >
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

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          resetForm();
        }}
        title={editingStudent ? 'Edit Student' : 'Add Student'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input
              type="text"
              required
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              required={!editingStudent}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="input"
              placeholder={editingStudent ? 'Leave blank to keep current' : ''}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Section</label>
            <select
              required
              value={formData.section_id}
              onChange={(e) => handleSectionChange(e.target.value)}
              className="input"
            >
              <option value="">Select a section</option>
              {sections.map((section) => (
                <option key={section.id} value={section.id}>
                  {section.full_name || section.name}{section.teacher_name ? ` (incharge: ${section.teacher_name})` : ''}
                </option>
              ))}
            </select>
          </div>
          {/* School record (optional) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Roll No.</label>
              <input type="text" value={formData.roll_number} onChange={(e) => setFormData({ ...formData, roll_number: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Admission No.</label>
              <input type="text" value={formData.admission_number} onChange={(e) => setFormData({ ...formData, admission_number: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Guardian Name</label>
              <input type="text" value={formData.guardian_name} onChange={(e) => setFormData({ ...formData, guardian_name: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Guardian Phone</label>
              <input type="tel" value={formData.guardian_phone} onChange={(e) => setFormData({ ...formData, guardian_phone: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
              <input type="date" value={formData.date_of_birth} onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })} className="input" />
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
              {editingStudent ? 'Update' : 'Add'} Student
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete: first shows what the student still has */}
      <Modal isOpen={showDeleteConfirm} onClose={closeDeleteWindow} title="Delete student">
        {deleteRecords === null ? (
          <p className="text-sm text-gray-400">Checking the student's records...</p>
        ) : deleteRecords.length === 0 ? (
          <div className="space-y-4">
            <p className="text-sm text-gray-700">Delete {deletingStudent?.name}? This can't be undone.</p>
            <div className="flex justify-end gap-2">
              <button onClick={closeDeleteWindow} className="btn btn-secondary">Cancel</button>
              <button onClick={handleDeleteConfirm} disabled={isDeleting} className="btn btn-primary bg-red-600 hover:bg-red-700">
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-gray-700">{deletingStudent?.name} still has:</p>
            <ul className="list-disc ml-5 text-sm text-gray-700 space-y-1">
              {deleteRecords.map((record) => (
                <li key={record.label}>{record.label}</li>
              ))}
            </ul>
            <p className="text-sm text-red-700">Deleting {deletingStudent?.name} also deletes these records. This can't be undone.</p>
            <div className="flex justify-end gap-2">
              <button onClick={closeDeleteWindow} className="btn btn-secondary">Cancel</button>
              <button onClick={handleDeleteConfirm} disabled={isDeleting} className="btn btn-primary bg-red-600 hover:bg-red-700">
                {isDeleting ? 'Deleting...' : 'Delete student and these records'}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AdminStudents;

