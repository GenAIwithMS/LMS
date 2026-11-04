import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Trash2, Edit, BookOpen, Users, ListOrdered, ChevronRight, UserCheck, CalendarDays } from 'lucide-react';
import {
  getSchoolClass, getSchoolClasses, addClassSection, updateClassSection, deleteClassSection,
  addClassSubject, renameClassSubject, deleteClassSubject,
  getSubjectChapters, addSubjectChapter, updateSubjectChapter, deleteSubjectChapter, getTeachers, setSubjectTeacher,
  getTeacherSubjects,
} from '../../services/api';
import type { SchoolClassDetails, SchoolClassSummary, ClassSubject, SyllabusChapter, Teacher, TeacherSkills } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

// One class (for example Class 5), set up in steps:
// 1. sections and their class incharge, 2. the subjects the class studies,
// 3. who teaches each subject in each section, 4. a link to the timetable.
// True if the teacher teaches this subject (names compared without capitals or spaces at the ends)
const teachesSubject = (skills: string[], subjectName: string): boolean => {
  for (const skill of skills) {
    if (skill.trim().toLowerCase() === subjectName.trim().toLowerCase()) {
      return true;
    }
  }
  return false;
};

const AdminClassDetail: React.FC = () => {
  const { classId } = useParams();
  const navigate = useNavigate();
  const [schoolClass, setSchoolClass] = useState<SchoolClassDetails | null>(null);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  // Which section each teacher already leads (a teacher can be incharge of only one section)
  const [inchargeOf, setInchargeOf] = useState<Record<number, { sectionId: number; name: string }>>({});
  const [loading, setLoading] = useState(true);

  const [newSectionName, setNewSectionName] = useState('');
  const [newSubjectName, setNewSubjectName] = useState('');

  // Chapters window for one subject
  const [chapterSubject, setChapterSubject] = useState<ClassSubject | null>(null);
  const [chapters, setChapters] = useState<SyllabusChapter[]>([]);
  const [newChapterTitle, setNewChapterTitle] = useState('');

  // The subjects each teacher teaches, so the teacher lists show them first
  const [teacherSkills, setTeacherSkills] = useState<TeacherSkills[]>([]);

  useEffect(() => {
    fetchClass();
    fetchTeachers();
    fetchSkills();
  }, [classId]);

  const fetchSkills = async () => {
    try {
      const data = await getTeacherSubjects();
      setTeacherSkills(Array.isArray(data.teachers) ? data.teachers : []);
    } catch (error: any) {
      showError(error, 'Failed to load the subjects teachers teach');
    }
  };

  // Does this teacher teach this subject?
  const teacherTeaches = (teacherId: number, subjectName: string): boolean => {
    for (const row of teacherSkills) {
      if (row.teacher_id === teacherId) {
        return teachesSubject(row.subjects, subjectName);
      }
    }
    return false;
  };

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchClass = async () => {
    try {
      const data = await getSchoolClass(Number(classId));
      setSchoolClass(data);
      fetchIncharges();
    } catch (error: any) {
      showError(error, 'Failed to load the class');
    } finally {
      setLoading(false);
    }
  };

  const fetchIncharges = async () => {
    try {
      const classes: SchoolClassSummary[] = await getSchoolClasses();
      const leads: Record<number, { sectionId: number; name: string }> = {};
      for (const oneClass of classes) {
        for (const section of oneClass.sections) {
          if (section.incharge_id) {
            leads[section.incharge_id] = { sectionId: section.id, name: section.full_name };
          }
        }
      }
      setInchargeOf(leads);
    } catch (error: any) {
      showError(error, 'Failed to load the class incharges');
    }
  };

  const fetchTeachers = async () => {
    try {
      const data = await getTeachers();
      setTeachers(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load teachers');
    }
  };

  // ---------------- Sections

  const handleAddSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSectionName.trim()) return;
    try {
      await addClassSection(Number(classId), { name: newSectionName.trim() });
      showSuccess(`Section ${newSectionName.trim()} added`);
      setNewSectionName('');
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to add the section');
    }
  };

  const handleInchargeChange = async (sectionId: number, teacherId: string) => {
    try {
      await updateClassSection(sectionId, { incharge_id: teacherId ? Number(teacherId) : null });
      showSuccess('Class incharge updated');
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to change the class incharge');
    }
  };

  const handleDeleteSection = async (sectionId: number, name: string) => {
    if (!window.confirm(`Delete section ${name}?`)) return;
    try {
      await deleteClassSection(sectionId);
      showSuccess('Section deleted');
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to delete the section');
    }
  };

  // ---------------- Subjects

  const handleAddSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSubjectName.trim()) return;
    try {
      await addClassSubject(Number(classId), newSubjectName.trim());
      showSuccess(`${newSubjectName.trim()} added`);
      setNewSubjectName('');
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to add the subject');
    }
  };

  const handleRenameSubject = async (subject: ClassSubject) => {
    const newName = window.prompt('New name for the subject', subject.name);
    if (!newName || newName.trim() === subject.name) return;
    try {
      await renameClassSubject(subject.id, newName.trim());
      showSuccess('Subject renamed');
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to rename the subject');
    }
  };

  const handleDeleteSubject = async (subject: ClassSubject) => {
    if (!window.confirm(`Delete ${subject.name} and its chapters?`)) return;
    try {
      await deleteClassSubject(subject.id);
      showSuccess('Subject deleted');
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to delete the subject');
    }
  };

  // ---------------- Subject teachers

  // The teacher of a subject in a section, as text for the dropdown ("" when nobody)
  const findSubjectTeacher = (sectionId: number, subjectId: number): string => {
    if (!schoolClass) return '';
    for (const row of schoolClass.subject_teachers) {
      if (row.section_id === sectionId && row.subject_id === subjectId) {
        return String(row.teacher_id);
      }
    }
    return '';
  };

  const handleSubjectTeacherChange = async (sectionId: number, subjectId: number, teacherId: string) => {
    try {
      const data = await setSubjectTeacher(sectionId, subjectId, teacherId ? Number(teacherId) : null);
      showSuccess(data.message || 'Subject teacher updated');
      fetchClass();
      // Teaching it in a section adds it to the teacher's subjects
      fetchSkills();
    } catch (error: any) {
      // For example: the teacher is busy in another section in one of this subject's periods
      showError(error, 'Failed to change the subject teacher');
    }
  };

  // ---------------- Chapters

  const openChapters = async (subject: ClassSubject) => {
    setChapterSubject(subject);
    setNewChapterTitle('');
    await fetchChapters(subject.id);
  };

  const fetchChapters = async (subjectId: number) => {
    try {
      const data = await getSubjectChapters(subjectId);
      setChapters(Array.isArray(data.data) ? data.data : []);
    } catch (error: any) {
      showError(error, 'Failed to load chapters');
    }
  };

  const handleAddChapter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chapterSubject || !newChapterTitle.trim()) return;
    try {
      await addSubjectChapter(chapterSubject.id, { title: newChapterTitle.trim() });
      setNewChapterTitle('');
      fetchChapters(chapterSubject.id);
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to add the chapter');
    }
  };

  const handleRenameChapter = async (chapter: SyllabusChapter) => {
    const newTitle = window.prompt(`New title for chapter ${chapter.number}`, chapter.title);
    if (!newTitle || newTitle.trim() === chapter.title || !chapterSubject) return;
    try {
      await updateSubjectChapter(chapter.id, { title: newTitle.trim() });
      fetchChapters(chapterSubject.id);
    } catch (error: any) {
      showError(error, 'Failed to rename the chapter');
    }
  };

  const handleDeleteChapter = async (chapter: SyllabusChapter) => {
    if (!chapterSubject || !window.confirm(`Delete chapter ${chapter.number}: ${chapter.title}?`)) return;
    try {
      await deleteSubjectChapter(chapter.id);
      fetchChapters(chapterSubject.id);
      fetchClass();
    } catch (error: any) {
      showError(error, 'Failed to delete the chapter');
    }
  };

  if (loading || !schoolClass) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <button onClick={() => navigate('/admin/classes')} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1 mb-2">
          <ArrowLeft size={16} /> All classes
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{schoolClass.name}</h1>
        <p className="text-gray-600 mt-2">Set up the class in order: sections, subjects, subject teachers, then the timetable</p>
      </div>

      {/* 1. Sections */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Users size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">1. Sections &amp; Class Incharge</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Section</th>
                <th>Class Incharge</th>
                <th>Students</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {schoolClass.sections.length === 0 ? (
                <tr><td colSpan={4} className="text-center py-6 text-gray-500">No sections yet. Add one below.</td></tr>
              ) : (
                schoolClass.sections.map((section) => (
                  <tr key={section.id}>
                    <td className="font-semibold">{section.full_name}</td>
                    <td>
                      <select value={section.incharge_id ? String(section.incharge_id) : ''} onChange={(e) => handleInchargeChange(section.id, e.target.value)} className="input py-1">
                        <option value="">No incharge yet</option>
                        {teachers.map((teacher) => {
                          // A teacher who already leads another section can't be chosen here
                          const leads = inchargeOf[teacher.id];
                          const leadsOther = leads !== undefined && leads.sectionId !== section.id;
                          return (
                            <option key={teacher.id} value={teacher.id} disabled={leadsOther}>
                              {teacher.name} ({teacher.username}){leadsOther ? ` - incharge of ${leads.name}` : ''}
                            </option>
                          );
                        })}
                      </select>
                    </td>
                    <td>{section.student_count}</td>
                    <td>
                      <div className="flex items-center gap-1">
                        <button onClick={() => navigate(`/admin/sections/${section.id}`)} className="btn btn-secondary text-sm px-3 py-1 flex items-center gap-1">
                          Open section <ChevronRight size={14} />
                        </button>
                        <button onClick={() => handleDeleteSection(section.id, section.full_name)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete section">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <form onSubmit={handleAddSection} className="flex gap-2 mt-4">
          <input type="text" placeholder="New section, e.g. A" value={newSectionName} onChange={(e) => setNewSectionName(e.target.value)} className="input max-w-xs" />
          <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Add Section</button>
        </form>
      </div>

      {/* 2. Subjects */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">2. Subjects ({schoolClass.subjects.length})</h2>
        </div>
        <form onSubmit={handleAddSubject} className="flex gap-2 mb-4">
          <input type="text" placeholder="New subject, e.g. Maths" value={newSubjectName} onChange={(e) => setNewSubjectName(e.target.value)} className="input max-w-xs" />
          <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Add Subject</button>
        </form>
        {schoolClass.subjects.length === 0 ? (
          <p className="text-sm text-gray-500">No subjects yet. Add the subjects this class studies, e.g. English, Urdu, Maths.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {schoolClass.subjects.map((subject) => (
              <div key={subject.id} className="border border-gray-200 rounded-xl p-3">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-semibold text-gray-900">{subject.name}</div>
                    <div className="text-xs text-gray-500">{subject.chapter_count} chapters</div>
                  </div>
                  <div className="flex">
                    <button onClick={() => handleRenameSubject(subject)} className="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Rename"><Edit size={14} /></button>
                    <button onClick={() => handleDeleteSubject(subject)} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Delete"><Trash2 size={14} /></button>
                  </div>
                </div>
                <button onClick={() => openChapters(subject)} className="mt-2 text-sm text-primary-600 hover:underline flex items-center gap-1">
                  <ListOrdered size={14} /> Chapters
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Subject teachers: who teaches each subject in each section */}
      <div className="card">
        <div className="flex items-center gap-2 mb-1">
          <UserCheck size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">3. Subject Teachers</h2>
        </div>
        <p className="text-sm text-gray-500 mb-4">Choose who teaches each subject in each section.</p>
        {schoolClass.sections.length === 0 ? (
          <p className="text-sm text-gray-500">Add a section first (step 1).</p>
        ) : schoolClass.subjects.length === 0 ? (
          <p className="text-sm text-gray-500">Add subjects first (step 2).</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Subject</th>
                  {schoolClass.sections.map((section) => (
                    <th key={section.id}>{section.full_name}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {schoolClass.subjects.map((subject) => (
                  <tr key={subject.id}>
                    <td className="font-semibold">{subject.name}</td>
                    {schoolClass.sections.map((section) => (
                      <td key={section.id}>
                        <select
                          value={findSubjectTeacher(section.id, subject.id)}
                          onChange={(e) => handleSubjectTeacherChange(section.id, subject.id, e.target.value)}
                          className="input py-1 min-w-[10rem]"
                        >
                          <option value="">No teacher yet</option>
                          <optgroup label={`Teaches ${subject.name}`}>
                            {teachers.filter((teacher) => teacherTeaches(teacher.id, subject.name)).map((teacher) => (
                              <option key={teacher.id} value={teacher.id}>{teacher.name}</option>
                            ))}
                          </optgroup>
                          <optgroup label="Other teachers">
                            {teachers.filter((teacher) => !teacherTeaches(teacher.id, subject.name)).map((teacher) => (
                              <option key={teacher.id} value={teacher.id}>{teacher.name}</option>
                            ))}
                          </optgroup>
                        </select>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 4. Timetable */}
      <div className="card flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <CalendarDays size={20} className="text-primary-600" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">4. Timetable</h2>
            <p className="text-sm text-gray-500">Make each section's weekly timetable on the Timetable page</p>
          </div>
        </div>
        <button onClick={() => navigate('/admin/timetable')} className="btn btn-primary flex items-center gap-1">
          Open Timetable <ChevronRight size={16} />
        </button>
      </div>

      <Modal isOpen={chapterSubject !== null} onClose={() => setChapterSubject(null)} title={chapterSubject ? `${chapterSubject.name}: chapters` : ''}>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {chapters.length === 0 ? (
            <p className="text-sm text-gray-500">No chapters yet.</p>
          ) : (
            chapters.map((chapter) => (
              <div key={chapter.id} className="flex items-center justify-between border border-gray-100 rounded-lg px-3 py-2">
                <span className="text-sm"><span className="font-semibold">{chapter.number}.</span> {chapter.title}</span>
                <div className="flex">
                  <button onClick={() => handleRenameChapter(chapter)} className="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Rename"><Edit size={14} /></button>
                  <button onClick={() => handleDeleteChapter(chapter)} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Delete"><Trash2 size={14} /></button>
                </div>
              </div>
            ))
          )}
        </div>
        <form onSubmit={handleAddChapter} className="flex gap-2 mt-4">
          <input type="text" placeholder="Chapter title" value={newChapterTitle} onChange={(e) => setNewChapterTitle(e.target.value)} className="input" />
          <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Add</button>
        </form>
      </Modal>
    </div>
  );
};

export default AdminClassDetail;
