import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Trash2, Search, Settings, Activity, BookOpen, X } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getTeachers, addTeacher, updateTeacher, deleteTeacher, getSchoolClasses, getSchoolClass, setSubjectTeacher, getTeacherSubjects, addTeacherSubject, removeTeacherSubject } from '../../services/api';
import type { Teacher, SchoolClassSummary, SchoolClassDetails, TeacherSkills } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

// True if the teacher teaches this subject (names compared without capitals or spaces at the ends)
const teachesSubject = (skills: string[], subjectName: string): boolean => {
  for (const skill of skills) {
    if (skill.trim().toLowerCase() === subjectName.trim().toLowerCase()) {
      return true;
    }
  }
  return false;
};

const AdminTeachers: React.FC = () => {
  const navigate = useNavigate();
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showOptions, setShowOptions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingTeacher, setDeletingTeacher] = useState<Teacher | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const optionsRef = useRef<HTMLDivElement>(null);

  // The "Subjects" window: what one teacher teaches, and giving them more
  const [subjectsTeacher, setSubjectsTeacher] = useState<Teacher | null>(null);
  const [allClasses, setAllClasses] = useState<SchoolClassSummary[]>([]);
  const [classDetails, setClassDetails] = useState<Record<number, SchoolClassDetails>>({});
  const [loadingSubjects, setLoadingSubjects] = useState(false);
  const [pickClassId, setPickClassId] = useState('');
  const [pickSectionId, setPickSectionId] = useState('');
  const [pickSubjectId, setPickSubjectId] = useState('');

  // The subjects each teacher teaches (before any class), and every subject name in the school
  const [teacherSkills, setTeacherSkills] = useState<TeacherSkills[]>([]);
  const [subjectNames, setSubjectNames] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
  });

  useEffect(() => {
    fetchTeachers();
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    try {
      const data = await getTeacherSubjects();
      setTeacherSkills(Array.isArray(data.teachers) ? data.teachers : []);
      setSubjectNames(Array.isArray(data.subject_names) ? data.subject_names : []);
    } catch (error: any) {
      showError(error, 'Failed to load the subjects teachers teach');
    }
  };

  // The subjects one teacher teaches
  const skillsOf = (teacherId: number): string[] => {
    for (const row of teacherSkills) {
      if (row.teacher_id === teacherId) {
        return row.subjects;
      }
    }
    return [];
  };

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

  // The spinner shows only on the first load. Returns the list, so a new teacher can be found in it.
  const fetchTeachers = async (): Promise<Teacher[]> => {
    let list: Teacher[] = [];
    try {
      const data = await getTeachers();
      if (Array.isArray(data)) {
        list = data;
      } else if (data.teacher) {
        list = [data.teacher];
      }
      setTeachers(list);
    } catch (error) {
      toast.error('Failed to fetch teachers');
    } finally {
      setLoading(false);
    }
    return list;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTeacher) {
        await updateTeacher(editingTeacher.id, formData);
        showSuccess('Teacher updated successfully');
        setIsModalOpen(false);
        resetForm();
        fetchTeachers();
      } else {
        const newUsername = formData.username.trim();
        await addTeacher(formData);
        showSuccess('Teacher added successfully');
        setIsModalOpen(false);
        resetForm();
        const list = await fetchTeachers();
        await fetchSkills();
        // Open the new teacher's Subjects window straight away, so their subjects can be added now
        let newTeacher: Teacher | null = null;
        for (const teacher of list) {
          if (teacher.username === newUsername) {
            newTeacher = teacher;
          }
        }
        if (newTeacher) {
          openSubjects(newTeacher);
        } else {
          toast.success('Now add their subjects with the Subjects button');
        }
      }
    } catch (error: any) {
      showError(error, 'Failed to save teacher');
    }
  };

  const handleEdit = (teacher: Teacher) => {
    setEditingTeacher(teacher);
    setFormData({
      name: teacher.name || '',
      username: teacher.username || '',
      email: teacher.email || '',
      password: '',
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (teacher: Teacher) => {
    setDeletingTeacher(teacher);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingTeacher) return;
    
    setIsDeleting(true);
    try {
      await deleteTeacher(deletingTeacher.id);
      showSuccess('Teacher deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingTeacher(null);
      fetchTeachers();
    } catch (error: any) {
      showError(error, 'Failed to delete teacher');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ name: '', username: '', email: '', password: '' });
    setEditingTeacher(null);
  };

  const filteredTeachers = teachers
    .filter(
      (teacher) =>
        teacher.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.username?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
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

  // ---------------- Subjects taught by a teacher

  // Every class that has sections, with its subjects and who teaches them
  const loadSubjectData = async () => {
    try {
      const classes: SchoolClassSummary[] = await getSchoolClasses();
      setAllClasses(Array.isArray(classes) ? classes : []);
      const details: Record<number, SchoolClassDetails> = {};
      for (const oneClass of classes) {
        if (oneClass.sections.length === 0) {
          continue;
        }
        const detail: SchoolClassDetails = await getSchoolClass(oneClass.id);
        details[oneClass.id] = detail;
      }
      setClassDetails(details);
    } catch (error: any) {
      showError(error, 'Failed to load the classes');
    } finally {
      setLoadingSubjects(false);
    }
  };

  const openSubjects = (teacher: Teacher) => {
    setSubjectsTeacher(teacher);
    setNewSkill('');
    setPickClassId('');
    setPickSectionId('');
    setPickSubjectId('');
    setLoadingSubjects(true);
    loadSubjectData();
  };

  // What the open teacher teaches now: "Maths in Class 5 - A"
  const getTeaching = () => {
    const rows: { sectionId: number; subjectId: number; text: string }[] = [];
    if (!subjectsTeacher) return rows;
    for (const classId of Object.keys(classDetails)) {
      const detail = classDetails[Number(classId)];
      for (const row of detail.subject_teachers) {
        if (row.teacher_id !== subjectsTeacher.id) {
          continue;
        }
        let subjectName = 'Subject';
        for (const subject of detail.subjects) {
          if (subject.id === row.subject_id) {
            subjectName = subject.name;
          }
        }
        let sectionName = 'Section';
        for (const section of detail.sections) {
          if (section.id === row.section_id) {
            sectionName = section.full_name;
          }
        }
        rows.push({ sectionId: row.section_id, subjectId: row.subject_id, text: `${subjectName} in ${sectionName}` });
      }
    }
    return rows;
  };

  // The section this teacher leads as class incharge, if any
  const getInchargeOf = (): string | null => {
    if (!subjectsTeacher) return null;
    for (const oneClass of allClasses) {
      for (const section of oneClass.sections) {
        if (section.incharge_id === subjectsTeacher.id) {
          return section.full_name;
        }
      }
    }
    return null;
  };

  const handleRemoveTeaching = async (sectionId: number, subjectId: number) => {
    try {
      const data = await setSubjectTeacher(sectionId, subjectId, null);
      showSuccess(data.message || 'Subject removed');
      loadSubjectData();
      fetchSkills();
    } catch (error: any) {
      showError(error, 'Failed to remove the subject');
    }
  };

  const handleAssignSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectsTeacher) return;
    if (!pickSectionId || !pickSubjectId) {
      toast.error('Choose a class, a section and a subject');
      return;
    }
    try {
      const data = await setSubjectTeacher(Number(pickSectionId), Number(pickSubjectId), subjectsTeacher.id);
      showSuccess(data.message || 'Subject assigned');
      setPickSubjectId('');
      loadSubjectData();
      // Teaching it in a section adds it to their subjects too
      fetchSkills();
    } catch (error: any) {
      // For example: the teacher is busy in another section in one of this subject's periods
      showError(error, 'Failed to assign the subject');
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectsTeacher) return;
    if (newSkill.trim() === '') {
      toast.error('Write or choose a subject, for example Urdu');
      return;
    }
    try {
      const data = await addTeacherSubject(subjectsTeacher.id, newSkill.trim());
      showSuccess(data.message || 'Subject added');
      setNewSkill('');
      fetchSkills();
    } catch (error: any) {
      showError(error, 'Failed to add the subject');
    }
  };

  const handleRemoveSkill = async (name: string) => {
    if (!subjectsTeacher) return;
    try {
      const data = await removeTeacherSubject(subjectsTeacher.id, name);
      showSuccess(data.message || 'Subject removed');
      fetchSkills();
    } catch (error: any) {
      // For example: they still teach it in a section
      showError(error, 'Failed to remove the subject');
    }
  };

  // A new class means its section and subject must be chosen again
  const changePickClass = (classId: string) => {
    setPickClassId(classId);
    setPickSectionId('');
    setPickSubjectId('');
  };

  // Who teaches a subject in a section now (for the option text)
  const currentTeacherName = (detail: SchoolClassDetails, sectionId: number, subjectId: number): string | null => {
    for (const row of detail.subject_teachers) {
      if (row.section_id === sectionId && row.subject_id === subjectId) {
        return row.teacher_name;
      }
    }
    return null;
  };

  // A subject option, with who teaches it in the chosen section now: "Maths (now: Sara)"
  const subjectLabel = (subjectId: number, subjectName: string): string => {
    if (!pickSectionId || !pickClassId) {
      return subjectName;
    }
    const now = currentTeacherName(classDetails[Number(pickClassId)], Number(pickSectionId), subjectId);
    if (now) {
      return `${subjectName} (now: ${now})`;
    }
    return subjectName;
  };

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
          <h1 className="text-3xl font-bold text-gray-900">Teachers</h1>
          <p className="text-gray-600 mt-2">Manage all teachers in the system</p>
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
                      <option value="email">Email</option>
                      <option value="username">Username</option>
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

          <button
            onClick={() => {
              resetForm();
              setIsModalOpen(true);
            }}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Add Teacher</span>
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Username</th>
              <th>Email</th>
              <th>Subjects</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredTeachers.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-500">
                  No teachers found
                </td>
              </tr>
            ) : (
              filteredTeachers.map((teacher) => (
                <tr key={teacher.id}>
                  <td>{teacher.id}</td>
                  <td>{teacher.name}</td>
                  <td>{teacher.username}</td>
                  <td>{teacher.email}</td>
                  <td>
                    {skillsOf(teacher.id).length === 0 ? (
                      <span className="text-gray-400">-</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {skillsOf(teacher.id).map((name) => (
                          <span key={name} className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 text-xs font-medium">{name}</span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      {/* The subjects this teacher teaches, and giving them more */}
                      <button
                        onClick={() => openSubjects(teacher)}
                        className="p-2 text-purple-600 hover:bg-purple-50 rounded"
                        title="Subjects"
                      >
                        <BookOpen size={18} />
                      </button>
                      {/* What this teacher has been doing (classes, diary, marks, recent actions) */}
                      <button
                        onClick={() => navigate(`/admin/teachers/${teacher.id}/activity`)}
                        className="p-2 text-green-600 hover:bg-green-50 rounded"
                        title="Activity"
                      >
                        <Activity size={18} />
                      </button>
                      <button
                        onClick={() => handleEdit(teacher)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <Edit size={18} />
                      </button>
                      <button
                        onClick={() => handleDeleteClick(teacher)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
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
        title={editingTeacher ? 'Edit Teacher' : 'Add Teacher'}
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
              required={!editingTeacher}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="input"
              placeholder={editingTeacher ? 'Leave blank to keep current' : ''}
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
              {editingTeacher ? 'Update' : 'Add'} Teacher
            </button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={subjectsTeacher !== null} onClose={() => setSubjectsTeacher(null)} title={subjectsTeacher ? `Subjects taught by ${subjectsTeacher.name}` : ''}>
        {loadingSubjects ? (
          <p className="text-sm text-gray-400">Loading...</p>
        ) : (
          <div className="space-y-5">
            {/* A. The subjects this teacher can teach (no class needed) */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-1">Subjects {subjectsTeacher?.name} teaches</h4>
              <p className="text-xs text-gray-500 mb-2">Add the subjects this teacher can teach. You can give them classes now or later.</p>
              {subjectsTeacher && skillsOf(subjectsTeacher.id).length === 0 ? (
                <p className="text-sm text-gray-500 mb-2">No subjects yet.</p>
              ) : (
                <div className="flex flex-wrap gap-2 mb-2">
                  {subjectsTeacher && skillsOf(subjectsTeacher.id).map((name) => (
                    <span key={name} className="flex items-center gap-1 px-2 py-1 rounded-full bg-purple-50 text-purple-700 text-sm font-medium">
                      {name}
                      <button type="button" onClick={() => handleRemoveSkill(name)} className="text-purple-400 hover:text-red-600" title={`Remove ${name}`}>
                        <X size={14} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
              <form onSubmit={handleAddSkill} className="flex gap-2">
                <input
                  type="text"
                  list="school-subject-names"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  placeholder="e.g. Urdu"
                  className="input"
                />
                <datalist id="school-subject-names">
                  {subjectNames.map((name) => (
                    <option key={name} value={name} />
                  ))}
                </datalist>
                <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Add</button>
              </form>
            </div>

            {/* B. Sections they teach in (optional, can be done later) */}
            <div className="border-t border-gray-100 pt-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Classes (optional, can be done later)</h4>
              <div className="text-sm mb-3">
                <span className="text-gray-500">Class incharge of: </span>
                <span className="font-semibold">{getInchargeOf() || 'none'}</span>
              </div>
              <h5 className="text-xs font-semibold text-gray-500 uppercase mb-2">Teaches now</h5>
              {getTeaching().length === 0 ? (
                <p className="text-sm text-gray-500">No subjects yet.</p>
              ) : (
                <div className="space-y-2">
                  {getTeaching().map((row) => (
                    <div key={`${row.sectionId}-${row.subjectId}`} className="flex items-center justify-between border border-gray-200 rounded-lg px-3 py-2">
                      <span className="text-sm">{row.text}</span>
                      <button onClick={() => handleRemoveTeaching(row.sectionId, row.subjectId)} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Remove">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <form onSubmit={handleAssignSubject} className="space-y-3">
              <h5 className="text-xs font-semibold text-gray-500 uppercase">Give a class</h5>
              {Object.keys(classDetails).length === 0 ? (
                <p className="text-sm text-gray-500">No class has sections yet. Add sections on the Classes page first.</p>
              ) : (
                <>
                  <select value={pickClassId} onChange={(e) => changePickClass(e.target.value)} className="input">
                    <option value="">Choose a class</option>
                    {allClasses.filter((oneClass) => classDetails[oneClass.id] !== undefined).map((oneClass) => (
                      <option key={oneClass.id} value={oneClass.id}>{oneClass.name}</option>
                    ))}
                  </select>

                  {pickClassId && classDetails[Number(pickClassId)] && (
                    classDetails[Number(pickClassId)].subjects.length === 0 ? (
                      <p className="text-sm text-gray-500">{classDetails[Number(pickClassId)].name} has no subjects yet. Add them on the Classes page.</p>
                    ) : (
                      <>
                        <select value={pickSectionId} onChange={(e) => setPickSectionId(e.target.value)} className="input">
                          <option value="">Choose a section</option>
                          {classDetails[Number(pickClassId)].sections.map((section) => (
                            <option key={section.id} value={section.id}>{section.full_name}</option>
                          ))}
                        </select>
                        <select value={pickSubjectId} onChange={(e) => setPickSubjectId(e.target.value)} className="input" disabled={!pickSectionId}>
                          <option value="">Choose a subject</option>
                          <optgroup label="Teaches">
                            {classDetails[Number(pickClassId)].subjects
                              .filter((subject) => subjectsTeacher !== null && teachesSubject(skillsOf(subjectsTeacher.id), subject.name))
                              .map((subject) => (
                                <option key={subject.id} value={subject.id}>{subjectLabel(subject.id, subject.name)}</option>
                              ))}
                          </optgroup>
                          <optgroup label="Other subjects">
                            {classDetails[Number(pickClassId)].subjects
                              .filter((subject) => subjectsTeacher === null || !teachesSubject(skillsOf(subjectsTeacher.id), subject.name))
                              .map((subject) => (
                                <option key={subject.id} value={subject.id}>{subjectLabel(subject.id, subject.name)}</option>
                              ))}
                          </optgroup>
                        </select>
                        <div className="flex justify-end">
                          <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Assign</button>
                        </div>
                      </>
                    )
                  )}
                </>
              )}
            </form>
          </div>
        )}
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingTeacher(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Teacher"
        itemName={deletingTeacher?.name || ''}
        itemType="teacher"
        effects={[
          'All subjects assigned to this teacher',
          'All sections managed by this teacher',
          'All assignments created by this teacher',
          'All attendance records marked by this teacher',
          'All results recorded by this teacher',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default AdminTeachers;

