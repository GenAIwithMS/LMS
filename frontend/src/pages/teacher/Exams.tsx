import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Upload, Download, PenLine, ClipboardList, Award } from 'lucide-react';
import {
  getExamTerms, getMyPapers, getPaperMarks, savePaperMarks, uploadQuestionPaper, downloadQuestionPaper,
  getMyClasses, getSectionResults, getReportCard, saveReportRemarks,
} from '../../services/api';
import type { ExamTerm, TeacherPaper, PaperMarksSheet, ClassSection, SectionResultSheet, QuestionStatus } from '../../types';
import { Modal } from '../../components/Modal';
import { ResultSheet } from '../../components/ResultSheet';
import { showError, showSuccess } from '../../utils/errorHandler';

// One row of the marks window
interface MarkRow {
  student_id: number;
  name: string;
  roll_number: string | null;
  marks: string;       // what the teacher typed, empty if nothing yet
  absent: boolean;
}

const QUESTION_STATUS_LABELS: Record<QuestionStatus, string> = {
  none: 'Not uploaded',
  submitted: 'Waiting for admin',
  approved: 'Approved',
  returned: 'Returned',
};

const QUESTION_STATUS_COLOURS: Record<QuestionStatus, string> = {
  none: 'bg-gray-100 text-gray-600',
  submitted: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  returned: 'bg-red-100 text-red-800',
};

// Exams for a teacher: the papers they mark in each term (enter marks, upload the
// question paper), and for the class incharge, their section's results and report card remarks.
const TeacherExams: React.FC = () => {
  const navigate = useNavigate();
  const [terms, setTerms] = useState<ExamTerm[]>([]);
  const [termId, setTermId] = useState<number | null>(null);
  const [papers, setPapers] = useState<TeacherPaper[]>([]);
  const [loading, setLoading] = useState(true);

  // Marks window
  const [sheet, setSheet] = useState<PaperMarksSheet | null>(null);
  const [markRows, setMarkRows] = useState<MarkRow[]>([]);

  // Question paper upload: one hidden file box, remembering which paper it's for
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploadPaperId, setUploadPaperId] = useState<number | null>(null);

  // Class incharge: section results and remarks
  const [inchargeSections, setInchargeSections] = useState<ClassSection[]>([]);
  const [resultSectionId, setResultSectionId] = useState<number | null>(null);
  const [resultSheet, setResultSheet] = useState<SectionResultSheet | null>(null);
  const [remarksStudent, setRemarksStudent] = useState<{ id: number; name: string } | null>(null);
  const [remarksText, setRemarksText] = useState('');

  useEffect(() => {
    fetchStart();
  }, []);

  useEffect(() => {
    if (termId !== null) {
      fetchPapers(termId);
    }
  }, [termId]);

  useEffect(() => {
    if (termId !== null && resultSectionId !== null) {
      fetchResults(termId, resultSectionId);
    } else {
      setResultSheet(null);
    }
  }, [termId, resultSectionId]);

  const fetchStart = async () => {
    try {
      const termData = await getExamTerms();
      const termList: ExamTerm[] = Array.isArray(termData) ? termData : [];
      setTerms(termList);
      if (termList.length > 0) {
        setTermId(termList[0].id);
      }

      const classData = await getMyClasses();
      const sections: ClassSection[] = Array.isArray(classData.incharge_of) ? classData.incharge_of : [];
      setInchargeSections(sections);
      if (sections.length > 0) {
        setResultSectionId(sections[0].id);
      }
    } catch (error: any) {
      showError(error, 'Failed to load the exams');
    } finally {
      setLoading(false);
    }
  };

  const fetchPapers = async (id: number) => {
    try {
      const data = await getMyPapers(id);
      setPapers(Array.isArray(data.papers) ? data.papers : []);
    } catch (error: any) {
      showError(error, 'Failed to load your papers');
    }
  };

  const fetchResults = async (id: number, sectionId: number) => {
    try {
      const data = await getSectionResults(id, sectionId);
      setResultSheet(data);
    } catch (error: any) {
      showError(error, 'Failed to load the results');
    }
  };

  // ---------------- Marks

  const openMarks = async (paper: TeacherPaper) => {
    try {
      const data: PaperMarksSheet = await getPaperMarks(paper.id, paper.section_id);
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
      setSheet(data);
    } catch (error: any) {
      showError(error, 'Failed to load the marks');
    }
  };

  const changeMarks = (studentId: number, value: string) => {
    const rows: MarkRow[] = [];
    for (const row of markRows) {
      if (row.student_id === studentId) {
        rows.push({ ...row, marks: value });
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
        let marks = row.marks;
        if (absent) {
          marks = '';
        }
        rows.push({ ...row, absent: absent, marks: marks });
      } else {
        rows.push(row);
      }
    }
    setMarkRows(rows);
  };

  const handleSaveMarks = async () => {
    if (!sheet) return;

    // Students with an empty box (and not absent) are left as they are
    const marks: { student_id: number; obtained_marks: number | null; is_absent: boolean }[] = [];
    for (const row of markRows) {
      if (row.absent) {
        marks.push({ student_id: row.student_id, obtained_marks: null, is_absent: true });
      } else if (row.marks !== '') {
        marks.push({ student_id: row.student_id, obtained_marks: Number(row.marks), is_absent: false });
      }
    }

    try {
      const data = await savePaperMarks(sheet.id, sheet.section_id, marks);
      showSuccess(data.message || 'Marks saved');
      setSheet(null);
      if (termId !== null) {
        fetchPapers(termId);
        if (resultSectionId !== null) {
          fetchResults(termId, resultSectionId);
        }
      }
    } catch (error: any) {
      showError(error, 'Failed to save the marks');
    }
  };

  // ---------------- Question paper

  const chooseFile = (paperId: number) => {
    setUploadPaperId(paperId);
    if (fileInput.current) {
      fileInput.current.value = '';
      fileInput.current.click();
    }
  };

  const handleFileChosen = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files[0];
    if (!file || uploadPaperId === null) return;
    try {
      const data = await uploadQuestionPaper(uploadPaperId, file);
      showSuccess(data.message || 'Question paper uploaded');
      if (termId !== null) {
        fetchPapers(termId);
      }
    } catch (error: any) {
      showError(error, 'Failed to upload the question paper');
    } finally {
      setUploadPaperId(null);
    }
  };

  const handleDownload = async (paperId: number) => {
    try {
      await downloadQuestionPaper(paperId);
    } catch (error: any) {
      showError(error, 'Failed to download the question paper');
    }
  };

  // ---------------- Remarks

  const openRemarks = async (studentId: number, name: string) => {
    if (termId === null) return;
    try {
      const card = await getReportCard(termId, studentId);
      setRemarksText(card.remarks || '');
      setRemarksStudent({ id: studentId, name: name });
    } catch (error: any) {
      showError(error, 'Failed to load the remarks');
    }
  };

  const handleSaveRemarks = async (e: React.FormEvent) => {
    e.preventDefault();
    if (termId === null || !remarksStudent) return;
    try {
      const data = await saveReportRemarks(termId, remarksStudent.id, remarksText);
      showSuccess(data.message || 'Remarks saved');
      setRemarksStudent(null);
    } catch (error: any) {
      showError(error, 'Failed to save the remarks');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  let term: ExamTerm | undefined = undefined;
  for (const item of terms) {
    if (item.id === termId) {
      term = item;
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Exams</h1>
        <p className="text-gray-600 mt-2">Enter marks for your papers, upload question papers, and see your class results</p>
      </div>

      {terms.length === 0 ? (
        <div className="card text-gray-500">No exam terms yet. The admin adds them.</div>
      ) : (
        <>
          <div className="card flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Exam term</label>
              <select value={termId !== null ? String(termId) : ''} onChange={(e) => setTermId(Number(e.target.value))} className="input">
                {terms.map((item) => (
                  <option key={item.id} value={item.id}>{item.name} ({item.session_name})</option>
                ))}
              </select>
            </div>
            {term && (
              <div className="text-sm text-gray-600">
                {term.start_date} to {term.end_date}
                {term.marks_deadline ? ` · Marks due by ${term.marks_deadline}` : ''}
              </div>
            )}
          </div>

          {term && term.is_closed && (
            <div className="p-4 rounded-xl bg-yellow-50 border border-yellow-200 text-yellow-800 flex items-center gap-2">
              <Lock size={18} /> Marks are locked for this term. You can still view them.
            </div>
          )}

          {/* My papers */}
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <ClipboardList size={20} className="text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">My Papers</h2>
            </div>
            {papers.length === 0 ? (
              <p className="text-sm text-gray-500">You have no papers to mark in this term. The admin sets up the papers for each class.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Class</th>
                      <th>Subject</th>
                      <th>Total / Passing</th>
                      <th>Exam Date</th>
                      <th>Marks Entered</th>
                      <th>Question Paper</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {papers.map((paper) => (
                      <tr key={`${paper.id}-${paper.section_id}`}>
                        <td>{paper.section_name}</td>
                        <td className="font-semibold">{paper.subject_name}</td>
                        <td>{paper.total_marks} / {paper.passing_marks}</td>
                        <td>{paper.exam_date || '-'}</td>
                        <td>{paper.marks_entered} / {paper.student_count}</td>
                        <td>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${QUESTION_STATUS_COLOURS[paper.question_status]}`}>
                            {QUESTION_STATUS_LABELS[paper.question_status]}
                          </span>
                          {paper.question_status === 'returned' && paper.review_note && (
                            <div className="text-xs text-red-600 mt-1">{paper.review_note}</div>
                          )}
                        </td>
                        <td>
                          <div className="flex flex-wrap items-center gap-1">
                            <button onClick={() => openMarks(paper)} className="btn btn-primary text-xs px-3 py-1 flex items-center gap-1">
                              <PenLine size={14} /> {term && term.is_closed ? 'View marks' : 'Enter marks'}
                            </button>
                            {paper.question_status !== 'approved' && (
                              <button onClick={() => chooseFile(paper.id)} className="btn btn-secondary text-xs px-3 py-1 flex items-center gap-1" title="Upload the question paper (PDF)">
                                <Upload size={14} /> Upload
                              </button>
                            )}
                            {paper.has_question_file && (
                              <button onClick={() => handleDownload(paper.id)} className="p-2 text-blue-600 hover:bg-blue-50 rounded" title="Download the question paper">
                                <Download size={14} />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <input ref={fileInput} type="file" accept="application/pdf" onChange={handleFileChosen} className="hidden" />
          </div>

          {/* Class incharge: results and remarks */}
          {inchargeSections.length > 0 && (
            <div className="card">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-2">
                  <Award size={20} className="text-primary-600" />
                  <h2 className="text-lg font-semibold text-gray-900">My Class Results</h2>
                </div>
                {inchargeSections.length > 1 && (
                  <select value={resultSectionId !== null ? String(resultSectionId) : ''} onChange={(e) => setResultSectionId(Number(e.target.value))} className="input max-w-xs">
                    {inchargeSections.map((section) => (
                      <option key={section.id} value={section.id}>{section.full_name}</option>
                    ))}
                  </select>
                )}
              </div>
              {!resultSheet ? (
                <p className="text-sm text-gray-400">Loading the results...</p>
              ) : (
                <>
                  <ResultSheet sheet={resultSheet} onOpenStudent={(id) => navigate(`/report-card/${termId}/${id}`)} />

                  <h3 className="font-semibold text-gray-900 mt-6 mb-2">Report Card Remarks</h3>
                  {term && term.is_published ? (
                    <p className="text-sm text-gray-500">This term's report cards are published, so the remarks can't be changed now.</p>
                  ) : (
                    <div className="space-y-2">
                      {resultSheet.students.map((student) => (
                        <div key={student.student_id} className="flex items-center justify-between border border-gray-100 rounded-lg px-3 py-2">
                          <span className="text-sm">{student.roll_number ? `${student.roll_number}. ` : ''}{student.name}</span>
                          <button onClick={() => openRemarks(student.student_id, student.name)} className="btn btn-secondary text-xs px-3 py-1 flex items-center gap-1">
                            <PenLine size={14} /> Edit remarks
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </>
      )}

      {/* Marks window */}
      <Modal isOpen={sheet !== null} onClose={() => setSheet(null)} title={sheet ? `${sheet.subject_name} marks · ${sheet.section_name} (out of ${sheet.total_marks})` : ''}>
        {sheet && (
          <div className="space-y-4">
            {sheet.is_closed && (
              <p className="text-sm text-yellow-700 flex items-center gap-1"><Lock size={14} /> Marks are locked. You can only look.</p>
            )}
            {markRows.length === 0 ? (
              <p className="text-sm text-gray-500">No students in this section.</p>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                <table className="table text-sm">
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
                            min={0}
                            max={Number(sheet.total_marks)}
                            step={0.5}
                            value={row.marks}
                            disabled={row.absent || sheet.is_closed}
                            onChange={(e) => changeMarks(row.student_id, e.target.value)}
                            className="input py-1 w-24"
                          />
                        </td>
                        <td>
                          <input type="checkbox" checked={row.absent} disabled={sheet.is_closed} onChange={(e) => changeAbsent(row.student_id, e.target.checked)} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p className="text-xs text-gray-500">Passing marks: {sheet.passing_marks}. Students left empty (and not absent) are not changed.</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setSheet(null)} className="btn btn-secondary">Close</button>
              {!sheet.is_closed && (
                <button onClick={handleSaveMarks} className="btn btn-primary">Save Marks</button>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Remarks window */}
      <Modal isOpen={remarksStudent !== null} onClose={() => setRemarksStudent(null)} title={remarksStudent ? `Remarks for ${remarksStudent.name}` : ''}>
        <form onSubmit={handleSaveRemarks} className="space-y-4">
          <textarea value={remarksText} onChange={(e) => setRemarksText(e.target.value)} rows={4} maxLength={1000} className="input" placeholder="e.g. Hard working. Needs to practise more in Maths." />
          <p className="text-xs text-gray-500">Leave it empty to remove the remarks.</p>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setRemarksStudent(null)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default TeacherExams;
