import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings, FileText, ClipboardList, BarChart3, Lock, Unlock, Eye, EyeOff, Download, Check, Undo2, Edit, Trash2, Plus } from 'lucide-react';
import {
  getExamTerm, updateExamTerm, getSchoolClasses, getTermPapers, setUpClassPapers, updateExamPaper, deleteExamPaper,
  downloadQuestionPaper, reviewQuestionPaper, getSectionResults, getTermAnalysis,
} from '../../services/api';
import type { ExamTerm, ExamPaper, SchoolClassSummary, SectionResultSheet, TermAnalysis, QuestionStatus } from '../../types';
import { Modal } from '../../components/Modal';
import { ResultSheet } from '../../components/ResultSheet';
import { showError, showSuccess } from '../../utils/errorHandler';

type Tab = 'papers' | 'questions' | 'results' | 'analysis';

const QUESTION_LABELS: Record<QuestionStatus, string> = {
  none: 'Not uploaded',
  submitted: 'Waiting for review',
  approved: 'Approved',
  returned: 'Returned',
};

const QUESTION_COLOURS: Record<QuestionStatus, string> = {
  none: 'bg-gray-100 text-gray-600',
  submitted: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  returned: 'bg-red-100 text-red-800',
};

// One exam term (for example First Term 2026-27), in tabs:
// - Settings & Papers: dates, marks deadline, lock and publish, and each class's papers
// - Question Papers: download, approve or return what the subject teachers uploaded
// - Results: a section's result sheet; open a student's report card from it
// - Analysis: averages and pass rates by section, subject and teacher
const AdminExamTerm: React.FC = () => {
  const { termId } = useParams();
  const navigate = useNavigate();

  const [term, setTerm] = useState<ExamTerm | null>(null);
  const [classes, setClasses] = useState<SchoolClassSummary[]>([]);
  const [papers, setPapers] = useState<ExamPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('papers');

  // Settings form
  const [settingsForm, setSettingsForm] = useState({ start_date: '', end_date: '', marks_deadline: '' });

  // Set up papers form
  const [setupClassId, setSetupClassId] = useState('');
  const [setupTotal, setSetupTotal] = useState('100');
  const [setupPassing, setSetupPassing] = useState('33');

  // Edit paper window
  const [paperToEdit, setPaperToEdit] = useState<ExamPaper | null>(null);
  const [paperForm, setPaperForm] = useState({ total_marks: '', passing_marks: '', exam_date: '' });

  // Delete paper window
  const [paperToDelete, setPaperToDelete] = useState<ExamPaper | null>(null);

  // Return question paper window
  const [paperToReturn, setPaperToReturn] = useState<ExamPaper | null>(null);
  const [returnNote, setReturnNote] = useState('');

  // Results tab
  const [resultClassId, setResultClassId] = useState('');
  const [resultSectionId, setResultSectionId] = useState('');
  const [resultSheet, setResultSheet] = useState<SectionResultSheet | null>(null);

  // Analysis tab
  const [analysisClassId, setAnalysisClassId] = useState('');
  const [analysis, setAnalysis] = useState<TermAnalysis | null>(null);

  useEffect(() => {
    fetchTerm();
    fetchClasses();
    fetchPapers();
  }, [termId]);

  useEffect(() => {
    if (tab === 'analysis') {
      fetchAnalysis();
    }
  }, [tab, analysisClassId]);

  useEffect(() => {
    if (tab === 'results' && resultSectionId) {
      fetchResults();
    }
  }, [tab, resultSectionId]);

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchTerm = async () => {
    try {
      const data = await getExamTerm(Number(termId));
      setTerm(data);
      setSettingsForm({
        start_date: data.start_date,
        end_date: data.end_date,
        marks_deadline: data.marks_deadline || '',
      });
    } catch (error: any) {
      showError(error, 'Failed to load the exam term');
    } finally {
      setLoading(false);
    }
  };

  const fetchClasses = async () => {
    try {
      const data = await getSchoolClasses();
      setClasses(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load the classes');
    }
  };

  const fetchPapers = async () => {
    try {
      const data = await getTermPapers(Number(termId));
      setPapers(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load the papers');
    }
  };

  const fetchResults = async () => {
    try {
      const data = await getSectionResults(Number(termId), Number(resultSectionId));
      setResultSheet(data);
    } catch (error: any) {
      showError(error, 'Failed to load the results');
    }
  };

  const fetchAnalysis = async () => {
    try {
      let classId: number | undefined = undefined;
      if (analysisClassId) {
        classId = Number(analysisClassId);
      }
      const data = await getTermAnalysis(Number(termId), classId);
      setAnalysis(data);
    } catch (error: any) {
      showError(error, 'Failed to load the analysis');
    }
  };

  // ---------------- Settings

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await updateExamTerm(Number(termId), {
        start_date: settingsForm.start_date,
        end_date: settingsForm.end_date,
        marks_deadline: settingsForm.marks_deadline ? settingsForm.marks_deadline : null,
      });
      showSuccess(data.message || 'Term updated');
      fetchTerm();
    } catch (error: any) {
      showError(error, 'Failed to update the term');
    }
  };

  const handleToggleLock = async () => {
    if (!term) return;
    try {
      await updateExamTerm(Number(termId), { is_locked: !term.is_locked });
      if (term.is_locked) {
        showSuccess('Marks unlocked');
      } else {
        showSuccess('Marks locked');
      }
      fetchTerm();
    } catch (error: any) {
      showError(error, 'Failed to change the lock');
    }
  };

  const handleTogglePublish = async () => {
    if (!term) return;
    try {
      await updateExamTerm(Number(termId), { is_published: !term.is_published });
      if (term.is_published) {
        showSuccess('Results unpublished');
      } else {
        showSuccess('Results published: students can now see their report cards');
      }
      fetchTerm();
    } catch (error: any) {
      showError(error, 'Failed to change publishing');
    }
  };

  // ---------------- Papers

  const handleSetUpPapers = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!setupClassId) return;
    try {
      const data = await setUpClassPapers(Number(termId), {
        class_id: Number(setupClassId),
        total_marks: Number(setupTotal),
        passing_marks: Number(setupPassing),
      });
      showSuccess(data.message || 'Papers added');
      fetchPapers();
      fetchTerm();
    } catch (error: any) {
      showError(error, 'Failed to set up the papers');
    }
  };

  const openEditPaper = (paper: ExamPaper) => {
    setPaperForm({
      total_marks: paper.total_marks,
      passing_marks: paper.passing_marks,
      exam_date: paper.exam_date || '',
    });
    setPaperToEdit(paper);
  };

  const handleEditPaper = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paperToEdit) return;
    try {
      const data = await updateExamPaper(paperToEdit.id, {
        total_marks: Number(paperForm.total_marks),
        passing_marks: Number(paperForm.passing_marks),
        exam_date: paperForm.exam_date ? paperForm.exam_date : null,
      });
      showSuccess(data.message || 'Paper updated');
      setPaperToEdit(null);
      fetchPapers();
    } catch (error: any) {
      showError(error, 'Failed to update the paper');
    }
  };

  const handleDeletePaper = async () => {
    if (!paperToDelete) return;
    try {
      const data = await deleteExamPaper(paperToDelete.id);
      showSuccess(data.message || 'Paper deleted');
      setPaperToDelete(null);
      fetchPapers();
      fetchTerm();
    } catch (error: any) {
      // For example: marks have already been entered for this paper
      showError(error, 'Failed to delete the paper');
      setPaperToDelete(null);
    }
  };

  // ---------------- Question papers

  const handleDownload = async (paper: ExamPaper) => {
    try {
      await downloadQuestionPaper(paper.id);
    } catch (error: any) {
      showError(error, 'Failed to download the question paper');
    }
  };

  const handleApprove = async (paper: ExamPaper) => {
    try {
      const data = await reviewQuestionPaper(paper.id, true);
      showSuccess(data.message || 'Question paper approved');
      fetchPapers();
    } catch (error: any) {
      showError(error, 'Failed to approve the question paper');
    }
  };

  const openReturn = (paper: ExamPaper) => {
    setReturnNote('');
    setPaperToReturn(paper);
  };

  const handleReturn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paperToReturn || !returnNote.trim()) return;
    try {
      const data = await reviewQuestionPaper(paperToReturn.id, false, returnNote.trim());
      showSuccess(data.message || 'Question paper returned');
      setPaperToReturn(null);
      fetchPapers();
    } catch (error: any) {
      showError(error, 'Failed to return the question paper');
    }
  };

  // ---------------- Results

  const handleResultClassChange = (classId: string) => {
    setResultClassId(classId);
    setResultSectionId('');
    setResultSheet(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!term) {
    return (
      <div className="space-y-4">
        <button onClick={() => navigate('/admin/exams')} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1">
          <ArrowLeft size={16} /> All exam terms
        </button>
        <div className="card text-gray-500">This exam term can't be shown.</div>
      </div>
    );
  }

  // Papers sorted by class, then subject
  const sortedPapers = [...papers];
  sortedPapers.sort((first, second) => {
    if (first.class_id !== second.class_id) {
      return first.class_id - second.class_id;
    }
    return first.subject_name.localeCompare(second.subject_name);
  });

  // Question papers: ones with something uploaded come first
  const questionPapers: ExamPaper[] = [];
  for (const paper of sortedPapers) {
    if (paper.has_question_file || paper.question_status !== 'none') {
      questionPapers.push(paper);
    }
  }
  for (const paper of sortedPapers) {
    if (!paper.has_question_file && paper.question_status === 'none') {
      questionPapers.push(paper);
    }
  }

  // The sections of the class chosen on the Results tab
  let resultSections: SchoolClassSummary['sections'] = [];
  const resultClass = classes.find((item) => String(item.id) === resultClassId);
  if (resultClass) {
    resultSections = resultClass.sections;
  }

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'papers', label: 'Settings & Papers', icon: <Settings size={16} /> },
    { key: 'questions', label: 'Question Papers', icon: <FileText size={16} /> },
    { key: 'results', label: 'Results', icon: <ClipboardList size={16} /> },
    { key: 'analysis', label: 'Analysis', icon: <BarChart3 size={16} /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <button onClick={() => navigate('/admin/exams')} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1 mb-2">
          <ArrowLeft size={16} /> All exam terms
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{term.name}</h1>
        <p className="text-gray-600 mt-2">Session {term.session_name} · {term.start_date} to {term.end_date}</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {term.is_locked && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Locked</span>
          )}
          {!term.is_locked && term.is_closed && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">Closed (deadline passed)</span>
          )}
          {!term.is_closed && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Open for marks</span>
          )}
          {term.is_published ? (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Published</span>
          ) : (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Not published</span>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-gray-200">
        {tabs.map((item) => (
          <button
            key={item.key}
            onClick={() => setTab(item.key)}
            className={`px-4 py-2 text-sm font-medium flex items-center gap-2 border-b-2 -mb-px ${tab === item.key ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}
          >
            {item.icon} {item.label}
          </button>
        ))}
      </div>

      {tab === 'papers' && (
        <>
          {/* Settings */}
          <div className="card space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
            <form onSubmit={handleSaveSettings} className="flex flex-wrap items-end gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Starts</label>
                <input type="date" required value={settingsForm.start_date} onChange={(e) => setSettingsForm({ ...settingsForm, start_date: e.target.value })} className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ends</label>
                <input type="date" required value={settingsForm.end_date} onChange={(e) => setSettingsForm({ ...settingsForm, end_date: e.target.value })} className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Marks deadline</label>
                <input type="date" value={settingsForm.marks_deadline} onChange={(e) => setSettingsForm({ ...settingsForm, marks_deadline: e.target.value })} className="input" />
              </div>
              <button type="submit" className="btn btn-primary">Save</button>
            </form>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="border border-gray-200 rounded-xl p-4">
                <button onClick={handleToggleLock} className="btn btn-secondary flex items-center gap-2">
                  {term.is_locked ? <><Unlock size={16} /> Unlock marks</> : <><Lock size={16} /> Lock marks</>}
                </button>
                <p className="text-xs text-gray-500 mt-2">Locked: teachers can't enter or change any marks for this term.</p>
              </div>
              <div className="border border-gray-200 rounded-xl p-4">
                <button onClick={handleTogglePublish} className="btn btn-secondary flex items-center gap-2">
                  {term.is_published ? <><EyeOff size={16} /> Unpublish</> : <><Eye size={16} /> Publish results</>}
                </button>
                <p className="text-xs text-gray-500 mt-2">Published: students can see their report cards for this term.</p>
              </div>
            </div>
          </div>

          {/* Papers */}
          <div className="card space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Papers</h2>
            <form onSubmit={handleSetUpPapers} className="flex flex-wrap items-end gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Class</label>
                <select required value={setupClassId} onChange={(e) => setSetupClassId(e.target.value)} className="input">
                  <option value="">Select a class</option>
                  {classes.map((item) => (
                    <option key={item.id} value={item.id}>{item.name} ({item.subject_count} subjects)</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Total marks</label>
                <input type="number" min="1" max="999" required value={setupTotal} onChange={(e) => setSetupTotal(e.target.value)} className="input w-28" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Passing marks</label>
                <input type="number" min="0" max="999" required value={setupPassing} onChange={(e) => setSetupPassing(e.target.value)} className="input w-28" />
              </div>
              <button type="submit" className="btn btn-primary flex items-center gap-1"><Plus size={16} /> Set up papers</button>
            </form>
            <p className="text-xs text-gray-500">Adds one paper for every subject of the class that doesn't have one yet.</p>

            {sortedPapers.length === 0 ? (
              <p className="text-sm text-gray-500">No papers yet. Choose a class above to set them up.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Class</th>
                      <th>Subject</th>
                      <th>Total</th>
                      <th>Passing</th>
                      <th>Exam date</th>
                      <th>Marks entered</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedPapers.map((paper) => (
                      <tr key={paper.id}>
                        <td>{paper.class_name}</td>
                        <td className="font-semibold">{paper.subject_name}</td>
                        <td>{paper.total_marks}</td>
                        <td>{paper.passing_marks}</td>
                        <td>{paper.exam_date || '-'}</td>
                        <td>{paper.marks_entered}</td>
                        <td>
                          <div className="flex">
                            <button onClick={() => openEditPaper(paper)} className="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit"><Edit size={16} /></button>
                            <button onClick={() => setPaperToDelete(paper)} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Delete"><Trash2 size={16} /></button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {tab === 'questions' && (
        <div className="card space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Question Papers</h2>
            <p className="text-sm text-gray-500">Subject teachers upload the question paper (PDF). Approve it, or return it with a note.</p>
          </div>
          {questionPapers.length === 0 ? (
            <p className="text-sm text-gray-500">No papers yet. Set them up on the Settings & Papers tab.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="table text-sm">
                <thead>
                  <tr>
                    <th>Class</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Uploaded by</th>
                    <th>Note</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {questionPapers.map((paper) => (
                    <tr key={paper.id}>
                      <td>{paper.class_name}</td>
                      <td className="font-semibold">{paper.subject_name}</td>
                      <td>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${QUESTION_COLOURS[paper.question_status]}`}>
                          {QUESTION_LABELS[paper.question_status]}
                        </span>
                      </td>
                      <td>{paper.uploaded_by || '-'}</td>
                      <td className="max-w-xs">{paper.review_note || '-'}</td>
                      <td>
                        {paper.has_question_file ? (
                          <div className="flex flex-wrap gap-1">
                            <button onClick={() => handleDownload(paper)} className="btn btn-secondary text-xs px-2 py-1 flex items-center gap-1"><Download size={14} /> Download</button>
                            {paper.question_status !== 'approved' && (
                              <button onClick={() => handleApprove(paper)} className="btn btn-primary text-xs px-2 py-1 flex items-center gap-1"><Check size={14} /> Approve</button>
                            )}
                            {/* An approved paper can still be sent back if something needs changing */}
                            {(paper.question_status === 'submitted' || paper.question_status === 'approved') && (
                              <button onClick={() => openReturn(paper)} className="btn btn-secondary text-xs px-2 py-1 flex items-center gap-1 text-red-600"><Undo2 size={14} /> Return</button>
                            )}
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === 'results' && (
        <div className="card space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Results</h2>
          <div className="flex flex-wrap gap-3">
            <select value={resultClassId} onChange={(e) => handleResultClassChange(e.target.value)} className="input max-w-xs">
              <option value="">Select a class</option>
              {classes.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
            <select value={resultSectionId} onChange={(e) => setResultSectionId(e.target.value)} className="input max-w-xs" disabled={!resultClassId}>
              <option value="">Select a section</option>
              {resultSections.map((section) => (
                <option key={section.id} value={section.id}>{section.full_name}</option>
              ))}
            </select>
          </div>
          {!resultSectionId ? (
            <p className="text-sm text-gray-500">Choose a class and section to see its result sheet. Click a student's name for the report card.</p>
          ) : !resultSheet ? (
            <p className="text-sm text-gray-400">Loading the results...</p>
          ) : (
            <ResultSheet sheet={resultSheet} onOpenStudent={(id) => navigate(`/report-card/${termId}/${id}`)} />
          )}
        </div>
      )}

      {tab === 'analysis' && (
        <div className="space-y-4">
          <div className="card flex flex-wrap items-center gap-3">
            <label className="text-sm text-gray-600">Class</label>
            <select value={analysisClassId} onChange={(e) => setAnalysisClassId(e.target.value)} className="input max-w-xs">
              <option value="">All classes</option>
              {classes.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </div>

          {!analysis ? (
            <p className="text-sm text-gray-400">Loading the analysis...</p>
          ) : analysis.sections.length === 0 ? (
            <div className="card text-gray-500">No papers or sections to analyse yet.</div>
          ) : (
            <>
              {analysis.sections.map((section) => (
                <div key={section.section_id} className="card space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h2 className="text-lg font-semibold text-gray-900">{section.section_name}</h2>
                    <span className="text-sm text-gray-600">{section.passed_count} of {section.student_count} passed</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="table text-sm">
                      <thead>
                        <tr>
                          <th>Subject</th>
                          <th>Teacher</th>
                          <th>Average %</th>
                          <th>Pass %</th>
                          <th>Highest</th>
                          <th>Marked</th>
                        </tr>
                      </thead>
                      <tbody>
                        {section.subjects.map((subject) => (
                          <tr key={subject.subject_name}>
                            <td className="font-semibold">{subject.subject_name}</td>
                            <td>{subject.teacher_name || '-'}</td>
                            <td>{subject.average_percentage !== null ? subject.average_percentage : '-'}</td>
                            <td>{subject.pass_percentage !== null ? subject.pass_percentage : '-'}</td>
                            <td>{subject.highest_marks !== null ? `${subject.highest_marks} / ${subject.total_marks}` : '-'}</td>
                            <td>{subject.marked_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Top students: </span>
                    {section.top_students.length === 0 ? (
                      <span className="text-gray-400">none yet</span>
                    ) : (
                      section.top_students.map((student, index) => (
                        <span key={index} className="mr-4">
                          <span className="font-semibold">{student.position}.</span> {student.name}
                          {student.percentage !== null ? ` (${student.percentage}%)` : ''}
                        </span>
                      ))
                    )}
                  </div>
                </div>
              ))}

              <div className="card space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">By Teacher</h2>
                {analysis.teachers.length === 0 ? (
                  <p className="text-sm text-gray-500">No subject teachers have been chosen yet.</p>
                ) : (
                  analysis.teachers.map((teacher) => (
                    <div key={teacher.teacher_name} className="border border-gray-200 rounded-xl p-4">
                      <div className="font-semibold text-gray-900 mb-2">{teacher.teacher_name}</div>
                      <div className="overflow-x-auto">
                        <table className="table text-sm">
                          <thead>
                            <tr>
                              <th>Section</th>
                              <th>Subject</th>
                              <th>Average %</th>
                              <th>Pass %</th>
                            </tr>
                          </thead>
                          <tbody>
                            {teacher.subjects.map((row, index) => (
                              <tr key={index}>
                                <td>{row.section_name}</td>
                                <td>{row.subject_name}</td>
                                <td>{row.average_percentage !== null ? row.average_percentage : '-'}</td>
                                <td>{row.pass_percentage !== null ? row.pass_percentage : '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      )}

      <Modal isOpen={paperToEdit !== null} onClose={() => setPaperToEdit(null)} title={paperToEdit ? `${paperToEdit.class_name} ${paperToEdit.subject_name} paper` : ''}>
        <form onSubmit={handleEditPaper} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Total marks</label>
              <input type="number" min="1" max="999" step="0.5" required value={paperForm.total_marks} onChange={(e) => setPaperForm({ ...paperForm, total_marks: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Passing marks</label>
              <input type="number" min="0" max="999" step="0.5" required value={paperForm.passing_marks} onChange={(e) => setPaperForm({ ...paperForm, passing_marks: e.target.value })} className="input" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Exam date (optional)</label>
            <input type="date" value={paperForm.exam_date} onChange={(e) => setPaperForm({ ...paperForm, exam_date: e.target.value })} className="input" />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setPaperToEdit(null)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={paperToDelete !== null} onClose={() => setPaperToDelete(null)} title="Delete paper">
        <p className="text-sm text-gray-700">
          Delete the {paperToDelete?.class_name} {paperToDelete?.subject_name} paper? A paper that already has marks can't be deleted.
        </p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setPaperToDelete(null)} className="btn btn-secondary">Cancel</button>
          <button onClick={handleDeletePaper} className="btn btn-primary bg-red-600 hover:bg-red-700">Delete</button>
        </div>
      </Modal>

      <Modal isOpen={paperToReturn !== null} onClose={() => setPaperToReturn(null)} title={paperToReturn ? `Return ${paperToReturn.class_name} ${paperToReturn.subject_name} question paper` : ''}>
        <form onSubmit={handleReturn} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">What should the teacher change?</label>
            <textarea required rows={3} value={returnNote} onChange={(e) => setReturnNote(e.target.value)} className="input" placeholder="e.g. Add a diagram question in section B" />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setPaperToReturn(null)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Return to teacher</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminExamTerm;
