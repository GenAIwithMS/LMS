import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { School, Users, BookOpen, CalendarRange, Plus, CheckCircle2 } from 'lucide-react';
import { getSchoolClasses, getAcademicSessions, addAcademicSession, makeSessionCurrent } from '../../services/api';
import type { SchoolClassSummary, AcademicSession } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

// The school at a glance: Class 1 to Class 10 with their sections, and the academic sessions.
const AdminClasses: React.FC = () => {
  const navigate = useNavigate();
  const [classes, setClasses] = useState<SchoolClassSummary[]>([]);
  const [sessions, setSessions] = useState<AcademicSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);
  const [sessionForm, setSessionForm] = useState({ name: '', start_date: '', end_date: '' });

  useEffect(() => {
    fetchAll();
  }, []);

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchAll = async () => {
    try {
      const classData = await getSchoolClasses();
      setClasses(Array.isArray(classData) ? classData : []);
      const sessionData = await getAcademicSessions();
      setSessions(Array.isArray(sessionData) ? sessionData : []);
    } catch (error: any) {
      showError(error, 'Failed to load the school structure');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSession = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addAcademicSession(sessionForm);
      showSuccess(`Session ${sessionForm.name} added`);
      setIsSessionModalOpen(false);
      setSessionForm({ name: '', start_date: '', end_date: '' });
      fetchAll();
    } catch (error: any) {
      showError(error, 'Failed to add the session');
    }
  };

  const handleMakeCurrent = async (session: AcademicSession) => {
    try {
      await makeSessionCurrent(session.id);
      showSuccess(`${session.name} is now the current session`);
      fetchAll();
    } catch (error: any) {
      showError(error, 'Failed to change the current session');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  let currentSessionName = 'No session yet';
  for (const session of sessions) {
    if (session.is_current) {
      currentSessionName = session.name;
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Classes</h1>
          <p className="text-gray-600 mt-2">Class 1 to Class 10: sections, class incharges, subjects and teachers</p>
        </div>
      </div>

      {/* Academic sessions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CalendarRange size={20} className="text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Academic Session</h2>
            <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-primary-100 text-primary-700">Current: {currentSessionName}</span>
          </div>
          <button onClick={() => setIsSessionModalOpen(true)} className="btn btn-secondary flex items-center gap-2 text-sm">
            <Plus size={16} />
            <span>Add Session</span>
          </button>
        </div>
        {sessions.length === 0 ? (
          <p className="text-sm text-gray-500">Add the current school year, for example 2026-27.</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {sessions.map((session) => (
              <div key={session.id} className={`px-4 py-2 rounded-xl border text-sm ${session.is_current ? 'border-primary-300 bg-primary-50' : 'border-gray-200'}`}>
                <div className="font-semibold text-gray-900 flex items-center gap-1">
                  {session.is_current && <CheckCircle2 size={14} className="text-primary-600" />}
                  {session.name}
                </div>
                <div className="text-gray-500">{session.start_date} to {session.end_date}</div>
                {!session.is_current && (
                  <button onClick={() => handleMakeCurrent(session)} className="text-primary-600 hover:underline text-xs mt-1">
                    Make current
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Classes 1 to 10 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {classes.map((schoolClass) => {
          let studentCount = 0;
          for (const section of schoolClass.sections) {
            studentCount = studentCount + section.student_count;
          }
          return (
            <button
              key={schoolClass.id}
              onClick={() => navigate(`/admin/classes/${schoolClass.id}`)}
              className="card text-left hover:shadow-lg hover:-translate-y-0.5 transition-all"
            >
              <div className="flex items-center gap-2 mb-3">
                <School size={20} className="text-primary-600" />
                <h3 className="text-lg font-bold text-gray-900">{schoolClass.name}</h3>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center gap-2"><Users size={14} /> {studentCount} students</div>
                <div className="flex items-center gap-2"><BookOpen size={14} /> {schoolClass.subject_count} subjects</div>
              </div>
              <div className="mt-3 flex flex-wrap gap-1">
                {schoolClass.sections.length === 0 ? (
                  <span className="text-xs text-gray-400">No sections yet</span>
                ) : (
                  schoolClass.sections.map((section) => (
                    <span key={section.id} className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-700" title={section.incharge_name ? `Incharge: ${section.incharge_name}` : 'No incharge yet'}>
                      {section.name}
                    </span>
                  ))
                )}
              </div>
            </button>
          );
        })}
      </div>

      <Modal isOpen={isSessionModalOpen} onClose={() => setIsSessionModalOpen(false)} title="Add Academic Session">
        <form onSubmit={handleAddSession} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input type="text" required placeholder="2026-27" value={sessionForm.name} onChange={(e) => setSessionForm({ ...sessionForm, name: e.target.value })} className="input" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Starts</label>
              <input type="date" required value={sessionForm.start_date} onChange={(e) => setSessionForm({ ...sessionForm, start_date: e.target.value })} className="input" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ends</label>
              <input type="date" required value={sessionForm.end_date} onChange={(e) => setSessionForm({ ...sessionForm, end_date: e.target.value })} className="input" />
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => setIsSessionModalOpen(false)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Add Session</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminClasses;
