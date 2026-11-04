import React, { useState, useEffect } from 'react';
import { CalendarDays, Printer } from 'lucide-react';
import { getMyTimetable, getMyClasses, getSectionTimetable } from '../services/api';
import type { Timetable, ClassSection } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { TimetableGrid } from '../components/TimetableGrid';
import { showError } from '../utils/errorHandler';

// The published timetable, as a full page:
// - a teacher sees their own week (every period they teach, with the section),
//   and the timetable of the section they lead as class incharge
// - a student sees their section's week, with the teacher of each period
const MyTimetable: React.FC = () => {
  const { userRole } = useAuth();
  const isTeacher = userRole === 'teacher';

  const [timetable, setTimetable] = useState<Timetable | null>(null);
  const [loading, setLoading] = useState(true);

  // For a class incharge: their section's timetable too
  const [inchargeSections, setInchargeSections] = useState<ClassSection[]>([]);
  const [view, setView] = useState<'mine' | 'class'>('mine');
  const [classTimetable, setClassTimetable] = useState<Timetable | null>(null);

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        const data = await getMyTimetable();
        setTimetable(data);
        if (isTeacher) {
          const myClasses = await getMyClasses();
          setInchargeSections(Array.isArray(myClasses.incharge_of) ? myClasses.incharge_of : []);
        }
      } catch (error: any) {
        showError(error, 'Failed to load the timetable');
      } finally {
        setLoading(false);
      }
    };
    fetchTimetable();
  }, []);

  const showClass = async () => {
    setView('class');
    if (classTimetable || inchargeSections.length === 0) return;
    try {
      const data = await getSectionTimetable(inchargeSections[0].id);
      setClassTimetable(data);
    } catch (error: any) {
      showError(error, 'Failed to load the class timetable');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!timetable || !timetable.is_published) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Timetable</h1>
        <div className="card flex items-center gap-3 text-gray-600">
          <CalendarDays size={24} className="text-gray-400" />
          The school hasn't published the timetable yet. It will appear here as soon as it does.
        </div>
      </div>
    );
  }

  let shown = timetable;
  let heading = isTeacher ? 'My weekly timetable' : `${timetable.section_name || 'My class'} timetable`;
  if (view === 'class' && classTimetable) {
    shown = classTimetable;
    heading = `${classTimetable.section_name} timetable`;
  }

  return (
    <div className="space-y-6">
      <div className="no-print flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Timetable</h1>
          <p className="text-gray-600 mt-2">Published by the school on {timetable.published_at}</p>
        </div>
        <button onClick={() => window.print()} className="btn btn-primary flex items-center gap-2"><Printer size={16} /> Print</button>
      </div>

      {isTeacher && inchargeSections.length > 0 && (
        <div className="no-print flex gap-2 border-b border-gray-200">
          <button onClick={() => setView('mine')} className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${view === 'mine' ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}>My Periods</button>
          <button onClick={showClass} className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${view === 'class' ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}>My Class ({inchargeSections[0].full_name})</button>
        </div>
      )}

      <div className="print-area card space-y-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2"><CalendarDays size={20} className="text-primary-600" /> {heading}</h2>
        {view === 'class' && !classTimetable ? (
          <p className="text-sm text-gray-400">Loading the class timetable...</p>
        ) : shown.slots.length === 0 ? (
          <p className="text-sm text-gray-500">{isTeacher && view === 'mine' ? 'You have no periods in the published timetable.' : 'No periods yet.'}</p>
        ) : (
          <TimetableGrid timetable={shown} showSection={isTeacher && view === 'mine'} />
        )}
      </div>
    </div>
  );
};

export default MyTimetable;
