import React, { useState, useEffect } from 'react';
import { School, UserCheck, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import { getMyClass } from '../../services/api';
import type { MyClass } from '../../types';
import { SyllabusList } from '../../components/SyllabusList';
import { showError } from '../../utils/errorHandler';

// A student's own class: section, roll number, class incharge,
// and each subject with its teacher and syllabus.
const StudentMyClass: React.FC = () => {
  const [myClass, setMyClass] = useState<MyClass | null>(null);
  const [loading, setLoading] = useState(true);
  const [openSubject, setOpenSubject] = useState<number | null>(null);

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

  if (loading || !myClass) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Class</h1>
        <p className="text-gray-600 mt-2">Your section, your teachers and your syllabus</p>
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

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Subjects ({myClass.subjects.length})</h2>
        </div>
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
    </div>
  );
};

export default StudentMyClass;
