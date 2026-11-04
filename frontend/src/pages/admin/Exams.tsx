import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, Plus, Trash2, CalendarDays } from 'lucide-react';
import { getAcademicSessions, getExamTerms, addExamTerm, deleteExamTerm } from '../../services/api';
import type { AcademicSession, ExamTerm } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';
import { todayText } from '../../utils/date';

// The exam terms of each session (First Term, Mid Term, Final Term).
// The admin adds a term here, then opens it to set up papers, review question
// papers, see results and publish report cards.
const AdminExams: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<AcademicSession[]>([]);
  const [terms, setTerms] = useState<ExamTerm[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // Add term window
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [termForm, setTermForm] = useState({ name: '', start_date: todayText(), end_date: todayText(), marks_deadline: '' });

  // Delete window
  const [termToDelete, setTermToDelete] = useState<ExamTerm | null>(null);

  useEffect(() => {
    fetchAll();
  }, []);

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchAll = async () => {
    try {
      const sessionData = await getAcademicSessions();
      const sessionList: AcademicSession[] = Array.isArray(sessionData) ? sessionData : [];
      setSessions(sessionList);

      // Start with the current session selected
      if (selectedSessionId === null) {
        const current = sessionList.find((session) => session.is_current);
        if (current) {
          setSelectedSessionId(current.id);
        } else if (sessionList.length > 0) {
          setSelectedSessionId(sessionList[0].id);
        }
      }

      const termData = await getExamTerms();
      setTerms(Array.isArray(termData) ? termData : []);
    } catch (error: any) {
      showError(error, 'Failed to load the exam terms');
    } finally {
      setLoading(false);
    }
  };

  const openAdd = () => {
    setTermForm({ name: '', start_date: todayText(), end_date: todayText(), marks_deadline: '' });
    setIsAddOpen(true);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedSessionId === null) return;
    try {
      const data = await addExamTerm({
        session_id: selectedSessionId,
        name: termForm.name.trim(),
        start_date: termForm.start_date,
        end_date: termForm.end_date,
        marks_deadline: termForm.marks_deadline ? termForm.marks_deadline : null,
      });
      showSuccess(data.message || 'Term added');
      setIsAddOpen(false);
      fetchAll();
    } catch (error: any) {
      showError(error, 'Failed to add the term');
    }
  };

  const handleDelete = async () => {
    if (!termToDelete) return;
    try {
      const data = await deleteExamTerm(termToDelete.id);
      showSuccess(data.message || 'Term deleted');
      setTermToDelete(null);
      fetchAll();
    } catch (error: any) {
      // For example: marks have already been entered for this term
      showError(error, 'Failed to delete the term');
      setTermToDelete(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // The terms of the chosen session only
  const sessionTerms: ExamTerm[] = [];
  for (const term of terms) {
    if (term.session_id === selectedSessionId) {
      sessionTerms.push(term);
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Exams</h1>
          <p className="text-gray-600 mt-2">Exam terms, papers, results and report cards</p>
        </div>
        {sessions.length > 0 && (
          <button onClick={openAdd} className="btn btn-primary flex items-center gap-2">
            <Plus size={18} /> Add Term
          </button>
        )}
      </div>

      {sessions.length === 0 ? (
        <div className="card text-gray-600">
          There is no academic session yet. Add one (for example 2026-27) on the{' '}
          <button onClick={() => navigate('/admin/classes')} className="text-primary-600 hover:underline">Classes</button> page first.
        </div>
      ) : (
        <>
          <div className="card flex flex-wrap items-center gap-3">
            <CalendarDays size={20} className="text-primary-600" />
            <label className="text-sm text-gray-600">Session</label>
            <select
              value={selectedSessionId !== null ? String(selectedSessionId) : ''}
              onChange={(e) => setSelectedSessionId(Number(e.target.value))}
              className="input max-w-xs"
            >
              {sessions.map((session) => (
                <option key={session.id} value={session.id}>
                  {session.name}{session.is_current ? ' (current)' : ''}
                </option>
              ))}
            </select>
          </div>

          {sessionTerms.length === 0 ? (
            <div className="card text-gray-500">No exam terms in this session yet. Click "Add Term" to add one.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sessionTerms.map((term) => (
                <div key={term.id} className="card hover:shadow-md transition-all">
                  <div className="flex items-start justify-between">
                    <button onClick={() => navigate(`/admin/exams/${term.id}`)} className="text-left flex items-center gap-3">
                      <GraduationCap size={28} className="text-primary-600" />
                      <div>
                        <div className="text-lg font-bold text-gray-900">{term.name}</div>
                        <div className="text-sm text-gray-500">{term.start_date} to {term.end_date}</div>
                      </div>
                    </button>
                    <button onClick={() => setTermToDelete(term)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete term">
                      <Trash2 size={16} />
                    </button>
                  </div>

                  <div className="mt-3 text-sm text-gray-600 space-y-1">
                    <div>Marks deadline: {term.marks_deadline || 'none'}</div>
                    <div>{term.paper_count} paper(s)</div>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    {term.is_locked && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Locked</span>
                    )}
                    {!term.is_locked && term.is_closed && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">Closed (deadline passed)</span>
                    )}
                    {term.is_published ? (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Published</span>
                    ) : (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Not published</span>
                    )}
                  </div>

                  <button onClick={() => navigate(`/admin/exams/${term.id}`)} className="btn btn-secondary text-sm mt-4 w-full">
                    Open
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      <Modal isOpen={isAddOpen} onClose={() => setIsAddOpen(false)} title="Add Exam Term">
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              required
              list="term-names"
              placeholder="First Term"
              value={termForm.name}
              onChange={(e) => setTermForm({ ...termForm, name: e.target.value })}
              className="input"
            />
            <datalist id="term-names">
              <option value="First Term" />
              <option value="Mid Term" />
              <option value="Final Term" />
            </datalist>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Starts</label>
              <input type="date" required value={termForm.start_date} onChange={(e) => setTermForm({ ...termForm, start_date: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ends</label>
              <input type="date" required value={termForm.end_date} onChange={(e) => setTermForm({ ...termForm, end_date: e.target.value })} className="input" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Marks deadline (optional)</label>
            <input type="date" value={termForm.marks_deadline} onChange={(e) => setTermForm({ ...termForm, marks_deadline: e.target.value })} className="input" />
            <p className="text-xs text-gray-500 mt-1">After this day, teachers can't change marks.</p>
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setIsAddOpen(false)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Add Term</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={termToDelete !== null} onClose={() => setTermToDelete(null)} title="Delete exam term">
        <p className="text-sm text-gray-700">
          Delete {termToDelete?.name} and its papers? A term that already has marks can't be deleted.
        </p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setTermToDelete(null)} className="btn btn-secondary">Cancel</button>
          <button onClick={handleDelete} className="btn btn-primary bg-red-600 hover:bg-red-700">Delete</button>
        </div>
      </Modal>
    </div>
  );
};

export default AdminExams;
