import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { getSectionProgress } from '../services/api';
import type { SectionProgressSubject } from '../types';
import { showError } from '../utils/errorHandler';
import { SyllabusEditor } from './SyllabusEditor';

interface ProgressViewProps {
  sectionId: number;
  // Kept for the pages that pass it; who can edit is now decided by the server (can_edit)
  editableSubjectIds?: number[];
}

// How much of each subject's syllabus a section has covered.
// Open a subject to see its chapters and daily topics; its teacher can edit them there.
export const ProgressView: React.FC<ProgressViewProps> = ({ sectionId }) => {
  const [subjects, setSubjects] = useState<SectionProgressSubject[]>([]);
  const [loading, setLoading] = useState(true);
  const [openSubjectId, setOpenSubjectId] = useState<number | null>(null);

  useEffect(() => {
    fetchProgress();
  }, [sectionId]);

  const fetchProgress = async () => {
    try {
      const data = await getSectionProgress(sectionId);
      setSubjects(Array.isArray(data.subjects) ? data.subjects : []);
    } catch (error: any) {
      showError(error, 'Failed to load the syllabus progress');
    } finally {
      setLoading(false);
    }
  };

  const toggleSubject = (subjectId: number) => {
    if (openSubjectId === subjectId) {
      setOpenSubjectId(null);
    } else {
      setOpenSubjectId(subjectId);
    }
  };

  if (loading) {
    return <p className="text-sm text-gray-400">Loading the syllabus progress...</p>;
  }
  if (subjects.length === 0) {
    return <p className="text-sm text-gray-500">This class has no subjects yet.</p>;
  }

  return (
    <div className="space-y-3">
      {subjects.map((subject) => {
        const isOpen = openSubjectId === subject.subject_id;
        return (
          <div key={subject.subject_id} className="border border-gray-200 rounded-xl p-4">
            <button onClick={() => toggleSubject(subject.subject_id)} className="w-full text-left">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-semibold text-gray-900">{subject.subject_name}</span>
                  <span className="text-sm text-gray-500"> · {subject.teacher_name || 'no teacher yet'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  {subject.done_count} of {subject.chapter_count} chapters done
                  {subject.topic_count > 0 && ` · ${subject.topics_done}/${subject.topic_count} topics`}
                  {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>
              <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-2 bg-green-500 rounded-full" style={{ width: `${subject.percentage}%` }}></div>
              </div>
              <div className="text-xs text-gray-500 mt-1">{subject.percentage}% covered{subject.in_progress_count > 0 ? `, ${subject.in_progress_count} in progress` : ''}</div>
            </button>

            {isOpen && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <SyllabusEditor sectionId={sectionId} subjectId={subject.subject_id} onChanged={fetchProgress} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
