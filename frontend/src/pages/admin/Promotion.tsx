import React, { useState, useEffect } from 'react';
import { GraduationCap, ArrowUpCircle } from 'lucide-react';
import { getSchoolClasses, getExamTerms, getPromotionList, promoteStudents } from '../../services/api';
import type { SchoolClassSummary, ExamTerm, PromotionList } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

const RESULT_COLOURS: Record<string, string> = {
  Pass: 'bg-green-100 text-green-800',
  Fail: 'bg-red-100 text-red-800',
  Incomplete: 'bg-gray-100 text-gray-600',
};

// Promotion at the end of the session: choose a section, see each student's result
// (from a term, usually the Final), tick who moves up, and move them to a section of the next class.
const AdminPromotion: React.FC = () => {
  const [classes, setClasses] = useState<SchoolClassSummary[]>([]);
  const [terms, setTerms] = useState<ExamTerm[]>([]);
  const [loading, setLoading] = useState(true);

  const [classId, setClassId] = useState<number | null>(null);
  const [sectionId, setSectionId] = useState<number | null>(null);
  const [termId, setTermId] = useState<number | null>(null);

  const [promotion, setPromotion] = useState<PromotionList | null>(null);
  const [targetSectionId, setTargetSectionId] = useState<number | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  useEffect(() => {
    fetchStart();
  }, []);

  useEffect(() => {
    if (sectionId !== null) {
      fetchPromotion(sectionId, termId);
    } else {
      setPromotion(null);
    }
  }, [sectionId, termId]);

  const fetchStart = async () => {
    try {
      const classData = await getSchoolClasses();
      setClasses(Array.isArray(classData) ? classData : []);

      const termData = await getExamTerms();
      const termList: ExamTerm[] = Array.isArray(termData) ? termData : [];
      setTerms(termList);

      // Base the decision on the newest Final term, if there is one
      for (const term of termList) {
        if (term.name.toLowerCase().includes('final')) {
          setTermId(term.id);
          break;
        }
      }
    } catch (error: any) {
      showError(error, 'Failed to load the classes');
    } finally {
      setLoading(false);
    }
  };

  const fetchPromotion = async (id: number, chosenTermId: number | null) => {
    try {
      let data: PromotionList;
      if (chosenTermId !== null) {
        data = await getPromotionList(id, chosenTermId);
      } else {
        data = await getPromotionList(id);
      }
      setPromotion(data);

      // Tick the students the school suggests promoting
      const ticked: number[] = [];
      for (const student of data.students) {
        if (student.suggest_promote) {
          ticked.push(student.student_id);
        }
      }
      setSelected(ticked);

      if (data.target_sections.length > 0) {
        setTargetSectionId(data.target_sections[0].id);
      } else {
        setTargetSectionId(null);
      }
    } catch (error: any) {
      showError(error, 'Failed to load the students');
    }
  };

  const handleClassChange = (value: string) => {
    setSectionId(null);
    if (value) {
      setClassId(Number(value));
    } else {
      setClassId(null);
    }
  };

  const toggleStudent = (studentId: number) => {
    if (selected.includes(studentId)) {
      const kept: number[] = [];
      for (const id of selected) {
        if (id !== studentId) {
          kept.push(id);
        }
      }
      setSelected(kept);
    } else {
      setSelected([...selected, studentId]);
    }
  };

  const selectAll = () => {
    if (!promotion) return;
    const all: number[] = [];
    for (const student of promotion.students) {
      all.push(student.student_id);
    }
    setSelected(all);
  };

  const handlePromote = async () => {
    if (sectionId === null || targetSectionId === null) return;
    try {
      const data = await promoteStudents(sectionId, { target_section_id: targetSectionId, student_ids: selected });
      showSuccess(data.message || 'Students promoted');
      setIsConfirmOpen(false);
      fetchPromotion(sectionId, termId);
    } catch (error: any) {
      showError(error, 'Failed to promote the students');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  let chosenClass: SchoolClassSummary | undefined = undefined;
  for (const item of classes) {
    if (item.id === classId) {
      chosenClass = item;
    }
  }

  let targetName = '';
  if (promotion) {
    for (const target of promotion.target_sections) {
      if (target.id === targetSectionId) {
        targetName = target.full_name;
      }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Promotion</h1>
        <p className="text-gray-600 mt-2">
          At the end of the session, move the students who passed to the next class. Students who are kept back stay in their section.
        </p>
      </div>

      <div className="card grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm text-gray-600 mb-1">Class</label>
          <select value={classId !== null ? String(classId) : ''} onChange={(e) => handleClassChange(e.target.value)} className="input">
            <option value="">Choose a class</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>{item.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Section</label>
          <select value={sectionId !== null ? String(sectionId) : ''} onChange={(e) => setSectionId(e.target.value ? Number(e.target.value) : null)} className="input" disabled={!chosenClass}>
            <option value="">Choose a section</option>
            {chosenClass && chosenClass.sections.map((section) => (
              <option key={section.id} value={section.id}>{section.full_name} ({section.student_count} students)</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Based on the results of</label>
          <select value={termId !== null ? String(termId) : ''} onChange={(e) => setTermId(e.target.value ? Number(e.target.value) : null)} className="input">
            <option value="">No term (decide by hand)</option>
            {terms.map((term) => (
              <option key={term.id} value={term.id}>{term.name} ({term.session_name})</option>
            ))}
          </select>
        </div>
      </div>

      {promotion && (
        <div className="card space-y-4">
          <div className="flex items-center gap-2">
            <GraduationCap size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">{promotion.section_name}</h2>
          </div>

          {promotion.is_last_class ? (
            <p className="text-sm text-gray-600">Class 10 is the last class; students can't be promoted further.</p>
          ) : promotion.students.length === 0 ? (
            <p className="text-sm text-gray-500">No students in this section.</p>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-3">
                <label className="text-sm text-gray-600">Move to</label>
                {promotion.target_sections.length === 0 ? (
                  <span className="text-sm text-orange-600">Add a section to {promotion.next_class_name} on the Classes page first.</span>
                ) : (
                  <select value={targetSectionId !== null ? String(targetSectionId) : ''} onChange={(e) => setTargetSectionId(Number(e.target.value))} className="input max-w-xs">
                    {promotion.target_sections.map((target) => (
                      <option key={target.id} value={target.id}>{target.full_name}</option>
                    ))}
                  </select>
                )}
                <button onClick={selectAll} className="btn btn-secondary text-sm">Select all</button>
                <button onClick={() => setSelected([])} className="btn btn-secondary text-sm">Select none</button>
              </div>

              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Promote</th>
                      <th>Roll</th>
                      <th>Name</th>
                      <th>Result</th>
                      <th>%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {promotion.students.map((student) => (
                      <tr key={student.student_id}>
                        <td>
                          <input type="checkbox" checked={selected.includes(student.student_id)} onChange={() => toggleStudent(student.student_id)} />
                        </td>
                        <td>{student.roll_number || '-'}</td>
                        <td>{student.name}</td>
                        <td>
                          {student.result ? (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${RESULT_COLOURS[student.result]}`}>{student.result}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td>{student.percentage !== null ? student.percentage : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <button
                onClick={() => setIsConfirmOpen(true)}
                disabled={selected.length === 0 || targetSectionId === null}
                className="btn btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                <ArrowUpCircle size={16} /> Promote {selected.length} student{selected.length === 1 ? '' : 's'}
              </button>
            </>
          )}
        </div>
      )}

      <Modal isOpen={isConfirmOpen} onClose={() => setIsConfirmOpen(false)} title="Promote students">
        <p className="text-sm text-gray-700">
          Move {selected.length} student{selected.length === 1 ? '' : 's'} from {promotion ? promotion.section_name : ''} to {targetName}?
        </p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setIsConfirmOpen(false)} className="btn btn-secondary">Cancel</button>
          <button onClick={handlePromote} className="btn btn-primary">Promote</button>
        </div>
      </Modal>
    </div>
  );
};

export default AdminPromotion;
