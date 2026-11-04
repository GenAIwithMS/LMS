import React, { useState, useEffect } from 'react';
import { School, UserCheck, BookOpen, ChevronDown, ChevronUp, CalendarDays, PenSquare, ListChecks } from 'lucide-react';
import { getMyClass, getMyTimetable } from '../../services/api';
import type { MyClass, Timetable } from '../../types';
import { SyllabusList } from '../../components/SyllabusList';
import { TimetableGrid } from '../../components/TimetableGrid';
import { DiaryView } from '../../components/DiaryView';
import { ProgressView } from '../../components/ProgressView';
import { showError } from '../../utils/errorHandler';

type Tab = 'subjects' | 'timetable' | 'diary' | 'progress';

// A student's own class: section, roll number and class incharge, then in tabs:
// subjects with their teachers and syllabus, the weekly timetable, the daily diary
// (classwork and homework), and how much of each subject's syllabus is covered.
const StudentMyClass: React.FC = () => {
  const [myClass, setMyClass] = useState<MyClass | null>(null);
  const [loading, setLoading] = useState(true);
  const [openSubject, setOpenSubject] = useState<number | null>(null);
  const [tab, setTab] = useState<Tab>('subjects');
  const [timetable, setTimetable] = useState<Timetable | null>(null);

  useEffect(() => {
    const fetchMyClass = async () => {
      try {
        setLoading(true);
        const data = await getMyClass();
        setMyClass(data);
      } catch (error: any) {
        showError(error, 'Failed to load your class');
      } finally {
        setLoading(false);
      }
    };
    fetchMyClass();
  }, []);

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        const data = await getMyTimetable();
        setTimetable(data);
      } catch (error: any) {
        showError(error, 'Failed to load the timetable');
      }
    };
    if (tab === 'timetable' && !timetable) {
      fetchTimetable();
    }
  }, [tab]);

  if (loading || !myClass) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'subjects', label: 'Subjects', icon: <BookOpen size={16} /> },
    { key: 'timetable', label: 'Timetable', icon: <CalendarDays size={16} /> },
    { key: 'diary', label: 'Diary', icon: <PenSquare size={16} /> },
    { key: 'progress', label: 'Syllabus Progress', icon: <ListChecks size={16} /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Class</h1>
        <p className="text-gray-600 mt-2">Your section, teachers, timetable, diary and syllabus</p>
      </div>

      <div className="card flex flex-wrap gap-8">
        <div className="flex items-center gap-3">
          <School size={28} className="text-primary-600" />
          <div>
            <div className="text-sm text-gray-500">Class</div>
            <div className="text-xl font-bold text-gray-900">{myClass.section_name || 'Not placed in a class yet'}</div>
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Roll No.</div>
          <div className="text-xl font-bold text-gray-900">{myClass.roll_number || '-'}</div>
        </div>
        <div className="flex items-center gap-3">
          <UserCheck size={28} className="text-primary-600" />
          <div>
            <div className="text-sm text-gray-500">Class Incharge</div>
            <div className="text-xl font-bold text-gray-900">{myClass.incharge_name || 'Not chosen yet'}</div>
          </div>
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

      {tab === 'subjects' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Subjects ({myClass.subjects.length})</h2>
          {myClass.subjects.length === 0 ? (
            <p className="text-sm text-gray-500">Your class has no subjects yet.</p>
          ) : (
            <div className="space-y-3">
              {myClass.subjects.map((subject) => {
                const isOpen = openSubject === subject.subject_id;
                return (
                  <div key={subject.subject_id} className="border border-gray-200 rounded-xl p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-gray-900">{subject.subject_name}</div>
                        <div className="text-sm text-gray-500">Teacher: {subject.teacher_name || 'not chosen yet'}</div>
                      </div>
                      <button onClick={() => setOpenSubject(isOpen ? null : subject.subject_id)} className="btn btn-secondary text-sm flex items-center gap-1">
                        Syllabus {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </button>
                    </div>
                    {isOpen && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <SyllabusList subjectId={subject.subject_id} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {tab === 'timetable' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Weekly Timetable</h2>
          {!timetable ? (
            <p className="text-sm text-gray-400">Loading the timetable...</p>
          ) : !timetable.is_published || timetable.slots.length === 0 ? (
            <p className="text-sm text-gray-500">The school hasn't published your timetable yet.</p>
          ) : (
            <TimetableGrid timetable={timetable} />
          )}
        </div>
      )}

      {tab === 'diary' && myClass.section_id && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Daily Diary</h2>
          <DiaryView sectionId={myClass.section_id} />
        </div>
      )}

      {tab === 'progress' && myClass.section_id && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Syllabus Progress</h2>
          <ProgressView sectionId={myClass.section_id} />
        </div>
      )}
    </div>
  );
};

export default StudentMyClass;
