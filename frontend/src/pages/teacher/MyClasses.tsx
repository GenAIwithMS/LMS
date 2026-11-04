import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserCheck, BookOpen, Users, ChevronDown, ChevronUp, CalendarDays } from 'lucide-react';
import { getMyClasses, getMyTimetable } from '../../services/api';
import type { MyClasses, Timetable } from '../../types';
import { SyllabusList } from '../../components/SyllabusList';
import { TimetableGrid } from '../../components/TimetableGrid';
import { showError } from '../../utils/errorHandler';

// A teacher's own classes: their weekly timetable, the sections they lead as
// class incharge, and every subject they teach, with that subject's syllabus.
const TeacherMyClasses: React.FC = () => {
  const navigate = useNavigate();
  const [myClasses, setMyClasses] = useState<MyClasses | null>(null);
  const [loading, setLoading] = useState(true);
  const [openSyllabus, setOpenSyllabus] = useState<string | null>(null);   // "sectionId-subjectId"
  const [timetable, setTimetable] = useState<Timetable | null>(null);

  useEffect(() => {
    const fetchMyClasses = async () => {
      try {
        setLoading(true);
        const data = await getMyClasses();
        setMyClasses(data);
        const timetableData = await getMyTimetable();
        setTimetable(timetableData);
      } catch (error: any) {
        showError(error, 'Failed to load your classes');
      } finally {
        setLoading(false);
      }
    };
    fetchMyClasses();
  }, []);

  if (loading || !myClasses) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Classes</h1>
        <p className="text-gray-600 mt-2">The sections you lead and the subjects you teach</p>
      </div>

      {/* My week */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <CalendarDays size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">My Timetable</h2>
        </div>
        {!timetable || timetable.slots.length === 0 ? (
          <p className="text-sm text-gray-500">No periods yet. The admin sets the timetable for each section.</p>
        ) : (
          <TimetableGrid timetable={timetable} showSection={true} />
        )}
      </div>

      {/* Class incharge */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <UserCheck size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Class Incharge Of</h2>
        </div>
        {myClasses.incharge_of.length === 0 ? (
          <p className="text-sm text-gray-500">You are not the class incharge of any section.</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {myClasses.incharge_of.map((section) => (
              <button key={section.id} onClick={() => navigate(`/teacher/sections/${section.id}`)} className="px-4 py-3 rounded-xl border border-primary-200 bg-primary-50 text-left hover:shadow-md transition-all">
                <div className="font-semibold text-gray-900">{section.full_name}</div>
                <div className="text-sm text-gray-500 flex items-center gap-1"><Users size={14} /> {section.student_count} students</div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Subjects taught */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Subjects I Teach</h2>
        </div>
        {myClasses.teaching.length === 0 ? (
          <p className="text-sm text-gray-500">The admin hasn't given you any subjects yet.</p>
        ) : (
          <div className="space-y-3">
            {myClasses.teaching.map((item) => {
              const key = `${item.section_id}-${item.subject_id}`;
              const isOpen = openSyllabus === key;
              return (
                <div key={key} className="border border-gray-200 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-gray-900">{item.subject_name}</div>
                      <button onClick={() => navigate(`/teacher/sections/${item.section_id}`)} className="text-sm text-primary-600 hover:underline">
                        {item.section_name}
                      </button>
                      <span className="text-sm text-gray-500"> · {item.student_count} students · {item.chapter_count} chapters</span>
                    </div>
                    <button onClick={() => setOpenSyllabus(isOpen ? null : key)} className="btn btn-secondary text-sm flex items-center gap-1">
                      Syllabus {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>
                  {isOpen && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <SyllabusList subjectId={item.subject_id} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherMyClasses;
