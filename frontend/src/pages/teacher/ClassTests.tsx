import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, PenLine, ClipboardCheck } from 'lucide-react';
import {
  getMyClasses, getClassTests, addClassTest, getClassTest, updateClassTest,
  saveClassTestMarks, deleteClassTest, getSectionChapters,
} from '../../services/api';
import { useSearchParams } from 'react-router-dom';
import type { ClassTest, ClassTestDetails, TeachingItem, SyllabusChapter } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

// One row of the marks window
interface MarkRow {
  student_id: number;
  name: string;
  roll_number: string | null;
  marks: string;       // what the teacher typed, empty if nothing yet
  absent: boolean;
}

// Today's date like "2026-11-04"
const todayText = () => {
  return new Date().toLocaleDateString('en-CA');
};

// The class picker's value is "sectionId-subjectId", like "3-12"
const teachingKey = (sectionId: number, subjectId: number) => {
  return `${sectionId}-${subjectId}`;
};

// Class tests: quick tests a subject teacher takes in their section, and the marks.
const TeacherClassTests: React.FC = () => {
  const [tests, setTests] = useState<ClassTest[]>([]);
  const [teaching, setTeaching] = useState<TeachingItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Add test window
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [addForm, setAddForm] = useState({ teaching_key: '', title: '', date: todayText(), total_marks: '10', chapter_id: '' });
  const [addChapters, setAddChapters] = useState<SyllabusChapter[]>([]);
  // The syllabus topic a new test is on (when it comes from a done topic)
  const [fromTopic, setFromTopic] = useState<{ id: number; title: string } | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();

  // Edit test window
  const [editingTest, setEditingTest] = useState<ClassTest | null>(null);
  const [editForm, setEditForm] = useState({ title: '', date: '', total_marks: '', chapter_id: '' });
  const [editChapters, setEditChapters] = useState<SyllabusChapter[]>([]);

  // Marks window
  const [marksTest, setMarksTest] = useState<ClassTestDetails | null>(null);
  const [markRows, setMarkRows] = useState<MarkRow[]>([]);

  // Delete window
  const [deletingTest, setDeletingTest] = useState<ClassTest | null>(null);

  useEffect(() => {
    fetchAll();
  }, []);

  // Sent here from a done topic in the syllabus (?new=1&section=..&subject=..&chapter=..&topic=..&topicTitle=..):
  // open Add Test with the class, subject, chapter and topic filled in
  useEffect(() => {
    if (searchParams.get('new') !== '1' || teaching.length === 0) {
      return;
    }
    const sectionId = Number(searchParams.get('section'));
    const subjectId = Number(searchParams.get('subject'));
    const chapterId = searchParams.get('chapter') || '';
    const topicId = Number(searchParams.get('topic'));
    const topicTitle = searchParams.get('topicTitle') || '';
    // So a reload doesn't open it again
    setSearchParams({}, { replace: true });

    const openFromTopic = async () => {
      const chapters = await fetchChapters(sectionId, subjectId);
      setAddChapters(chapters);
      setAddForm({
        teaching_key: teachingKey(sectionId, subjectId),
        title: topicTitle ? `${topicTitle} quiz` : '',
        date: todayText(),
        total_marks: '10',
        chapter_id: chapterId,
      });
      if (topicId) {
        setFromTopic({ id: topicId, title: topicTitle });
      } else {
        setFromTopic(null);
      }
      setIsAddOpen(true);
    };
    openFromTopic();
  }, [teaching, searchParams]);

  const fetchAll = async () => {
    try {
      const classData = await getMyClasses();
      if (classData && Array.isArray(classData.teaching)) {
        setTeaching(classData.teaching);
      }
      await fetchTests();
    } catch (error: any) {
      showError(error, 'Failed to load your classes');
    } finally {
      setLoading(false);
    }
  };

  const fetchTests = async () => {
    try {
      const data = await getClassTests();
      setTests(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load the tests');
    }
  };

  // The section's own chapters for the subject (each section writes its own syllabus)
  const fetchChapters = async (sectionId: number, subjectId: number) => {
    try {
      const data = await getSectionChapters(sectionId, subjectId);
      if (Array.isArray(data.data)) {
        return data.data as SyllabusChapter[];
      }
    } catch (error: any) {
      showError(error, 'Failed to load the chapters');
    }
    return [];
  };

  // How many students the test's section has
  const studentCount = (test: ClassTest) => {
    for (const item of teaching) {
      if (item.section_id === test.section_id && item.subject_id === test.subject_id) {
        return item.student_count;
      }
    }
    return 0;
  };

  // ---------------- Add a test

  const openAdd = () => {
    setAddForm({ teaching_key: '', title: '', date: todayText(), total_marks: '10', chapter_id: '' });
    setAddChapters([]);
    setFromTopic(null);
    setIsAddOpen(true);
  };

  const handleAddTeachingChange = async (key: string) => {
    setAddForm({ ...addForm, teaching_key: key, chapter_id: '' });
    setAddChapters([]);
    for (const item of teaching) {
      if (teachingKey(item.section_id, item.subject_id) === key) {
        const chapters = await fetchChapters(item.section_id, item.subject_id);
        setAddChapters(chapters);
      }
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    let chosen: TeachingItem | null = null;
    for (const item of teaching) {
      if (teachingKey(item.section_id, item.subject_id) === addForm.teaching_key) {
        chosen = item;
      }
    }
    if (!chosen) return;

    try {
      await addClassTest({
        section_id: chosen.section_id,
        subject_id: chosen.subject_id,
        title: addForm.title.trim(),
        date: addForm.date,
        total_marks: Number(addForm.total_marks),
        chapter_id: addForm.chapter_id ? Number(addForm.chapter_id) : null,
        topic_id: fromTopic ? fromTopic.id : null,
      });
      showSuccess(`Test '${addForm.title.trim()}' added`);
      setIsAddOpen(false);
      setFromTopic(null);
      fetchTests();
    } catch (error: any) {
      showError(error, 'Failed to add the test');
    }
  };

  // ---------------- Edit a test

  const openEdit = async (test: ClassTest) => {
    setEditingTest(test);
    setEditForm({
      title: test.title,
      date: test.date,
      total_marks: test.total_marks,
      chapter_id: test.chapter_id ? String(test.chapter_id) : '',
    });
    const chapters = await fetchChapters(test.section_id, test.subject_id);
    setEditChapters(chapters);
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTest) return;
    try {
      await updateClassTest(editingTest.id, {
        title: editForm.title.trim(),
        date: editForm.date,
        total_marks: Number(editForm.total_marks),
        chapter_id: editForm.chapter_id ? Number(editForm.chapter_id) : null,
      });
      showSuccess('Test updated');
      setEditingTest(null);
      fetchTests();
    } catch (error: any) {
      showError(error, 'Failed to update the test');
    }
  };

  // ---------------- Enter marks

  const openMarks = async (test: ClassTest) => {
    try {
      const data: ClassTestDetails = await getClassTest(test.id);
      const rows: MarkRow[] = [];
      for (const student of data.students) {
        rows.push({
          student_id: student.student_id,
          name: student.name,
          roll_number: student.roll_number,
          marks: student.obtained_marks !== null ? student.obtained_marks : '',
          absent: student.is_absent,
        });
      }
      setMarkRows(rows);
      setMarksTest(data);
    } catch (error: any) {
      showError(error, 'Failed to load the marks');
    }
  };

  const changeMarks = (studentId: number, marks: string) => {
    const rows: MarkRow[] = [];
    for (const row of markRows) {
      if (row.student_id === studentId) {
        rows.push({ ...row, marks: marks });
      } else {
        rows.push(row);
      }
    }
    setMarkRows(rows);
  };

  const changeAbsent = (studentId: number, absent: boolean) => {
    const rows: MarkRow[] = [];
    for (const row of markRows) {
      if (row.student_id === studentId) {
        // An absent student has no marks
        rows.push({ ...row, absent: absent, marks: absent ? '' : row.marks });
      } else {
        rows.push(row);
      }
    }
    setMarkRows(rows);
  };

  const handleSaveMarks = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!marksTest) return;

    // Students with an empty box (and not absent) are left as they are
    const marks: { student_id: number; obtained_marks: number | null }[] = [];
    for (const row of markRows) {
      if (row.absent) {
        marks.push({ student_id: row.student_id, obtained_marks: null });
      } else if (row.marks !== '') {
        marks.push({ student_id: row.student_id, obtained_marks: Number(row.marks) });
      }
    }
    if (marks.length === 0) {
      showError(new Error('Enter marks for at least one student'), 'Enter marks for at least one student');
      return;
    }

    try {
      await saveClassTestMarks(marksTest.id, marks);
      showSuccess('Marks saved');
      setMarksTest(null);
      fetchTests();
    } catch (error: any) {
      showError(error, 'Failed to save the marks');
    }
  };

  // ---------------- Delete a test

  const handleDelete = async () => {
    if (!deletingTest) return;
    try {
      await deleteClassTest(deletingTest.id);
      showSuccess('Test deleted');
      setDeletingTest(null);
      fetchTests();
    } catch (error: any) {
      showError(error, 'Failed to delete the test');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Class Tests</h1>
          <p className="text-gray-600 mt-2">Quick tests in your sections, and your students' marks</p>
        </div>
        <button onClick={openAdd} className="btn btn-primary flex items-center gap-2" disabled={teaching.length === 0}>
          <Plus size={18} /> Add Test
        </button>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <ClipboardCheck size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Tests ({tests.length})</h2>
        </div>
        {teaching.length === 0 ? (
          <p className="text-sm text-gray-500">The admin hasn't given you any subjects yet.</p>
        ) : tests.length === 0 ? (
          <p className="text-sm text-gray-500">No tests yet. Add one with the button above.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Title</th>
                  <th>Class</th>
                  <th>Subject</th>
                  <th>Chapter</th>
                  <th>Total</th>
                  <th>Marks Entered</th>
                  <th>Average</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tests.map((test) => (
                  <tr key={test.id}>
                    <td>{test.date}</td>
                    <td className="font-semibold">{test.title}</td>
                    <td>{test.section_name}</td>
                    <td>{test.subject_name}</td>
                    <td>
                      {test.chapter_title || '-'}
                      {test.topic_title ? ` · ${test.topic_title}` : ''}
                    </td>
                    <td>{test.total_marks}</td>
                    <td>{test.marks_entered} / {studentCount(test)}</td>
                    <td>{test.average !== null ? test.average : '-'}</td>
                    <td>
                      <div className="flex items-center gap-1">
                        {/* Marks can be entered once the test has taken place */}
                        <button
                          onClick={() => openMarks(test)}
                          disabled={test.date > todayText()}
                          title={test.date > todayText() ? `This test is on ${test.date}; marks can be entered from that day` : `Marks for ${test.title}`}
                          className="btn btn-secondary text-sm px-3 py-1 flex items-center gap-1 disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          <PenLine size={14} /> Marks
                        </button>
                        <button onClick={() => openEdit(test)} className="p-2 text-blue-600 hover:bg-blue-50 rounded" title="Edit test">
                          <Edit size={16} />
                        </button>
                        <button onClick={() => setDeletingTest(test)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete test">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add test */}
      <Modal isOpen={isAddOpen} onClose={() => { setIsAddOpen(false); setFromTopic(null); }} title="Add Class Test">
        <form onSubmit={handleAdd} className="space-y-4">
          {fromTopic && (
            <p className="text-sm text-primary-700 bg-primary-50 rounded-lg px-3 py-2">On topic: {fromTopic.title}</p>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Class and Subject</label>
            <select required value={addForm.teaching_key} onChange={(e) => handleAddTeachingChange(e.target.value)} className="input">
              <option value="">Select a class and subject</option>
              {teaching.map((item) => (
                <option key={teachingKey(item.section_id, item.subject_id)} value={teachingKey(item.section_id, item.subject_id)}>
                  {item.section_name} · {item.subject_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input type="text" required placeholder="Quiz 1" value={addForm.title} onChange={(e) => setAddForm({ ...addForm, title: e.target.value })} className="input" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
              <input type="date" required value={addForm.date} onChange={(e) => setAddForm({ ...addForm, date: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Total Marks</label>
              <input type="number" required min="1" max="999" value={addForm.total_marks} onChange={(e) => setAddForm({ ...addForm, total_marks: e.target.value })} className="input" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Chapter (optional)</label>
            <select value={addForm.chapter_id} onChange={(e) => setAddForm({ ...addForm, chapter_id: e.target.value })} className="input" disabled={addChapters.length === 0}>
              <option value="">No chapter</option>
              {addChapters.map((chapter) => (
                <option key={chapter.id} value={chapter.id}>{chapter.number}. {chapter.title}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setIsAddOpen(false)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Add Test</button>
          </div>
        </form>
      </Modal>

      {/* Edit test */}
      <Modal isOpen={editingTest !== null} onClose={() => setEditingTest(null)} title={editingTest ? `Edit: ${editingTest.title}` : ''}>
        <form onSubmit={handleEdit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input type="text" required value={editForm.title} onChange={(e) => setEditForm({ ...editForm, title: e.target.value })} className="input" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
              <input type="date" required value={editForm.date} onChange={(e) => setEditForm({ ...editForm, date: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Total Marks</label>
              <input type="number" required min="1" max="999" step="0.5" value={editForm.total_marks} onChange={(e) => setEditForm({ ...editForm, total_marks: e.target.value })} className="input" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Chapter (optional)</label>
            <select value={editForm.chapter_id} onChange={(e) => setEditForm({ ...editForm, chapter_id: e.target.value })} className="input">
              <option value="">No chapter</option>
              {editChapters.map((chapter) => (
                <option key={chapter.id} value={chapter.id}>{chapter.number}. {chapter.title}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setEditingTest(null)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      </Modal>

      {/* Enter marks */}
      <Modal isOpen={marksTest !== null} onClose={() => setMarksTest(null)} title={marksTest ? `${marksTest.title}: marks out of ${marksTest.total_marks}` : ''}>
        {marksTest && (
          <form onSubmit={handleSaveMarks} className="space-y-4">
            <p className="text-sm text-gray-500">{marksTest.section_name} · {marksTest.subject_name} · {marksTest.date}</p>
            {markRows.length === 0 ? (
              <p className="text-sm text-gray-500">This section has no students yet.</p>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Roll</th>
                      <th>Name</th>
                      <th>Marks</th>
                      <th>Absent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {markRows.map((row) => (
                      <tr key={row.student_id}>
                        <td>{row.roll_number || '-'}</td>
                        <td>{row.name}</td>
                        <td>
                          <input
                            type="number"
                            min="0"
                            max={marksTest.total_marks}
                            step="0.5"
                            value={row.marks}
                            disabled={row.absent}
                            onChange={(e) => changeMarks(row.student_id, e.target.value)}
                            className="input py-1 w-24"
                          />
                        </td>
                        <td>
                          <input type="checkbox" checked={row.absent} onChange={(e) => changeAbsent(row.student_id, e.target.checked)} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p className="text-xs text-gray-500">Students left empty (and not absent) are not changed.</p>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={() => setMarksTest(null)} className="btn btn-secondary">Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={markRows.length === 0}>Save Marks</button>
            </div>
          </form>
        )}
      </Modal>

      {/* Delete test */}
      <Modal isOpen={deletingTest !== null} onClose={() => setDeletingTest(null)} title="Delete Test">
        {deletingTest && (
          <div className="space-y-4">
            <p className="text-gray-700">
              Delete <span className="font-semibold">{deletingTest.title}</span> ({deletingTest.section_name} · {deletingTest.subject_name})?
              All marks entered for it will be deleted too.
            </p>
            <div className="flex justify-end gap-3">
              <button onClick={() => setDeletingTest(null)} className="btn btn-secondary">Cancel</button>
              <button onClick={handleDelete} className="btn bg-red-600 text-white hover:bg-red-700">Delete</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TeacherClassTests;
