import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { getSectionProgress, getSubjectProgress, updateChapterProgress } from '../services/api';
import type { SectionProgressSubject, SubjectProgress, ProgressStatus } from '../types';
import { showError } from '../utils/errorHandler';

interface ProgressViewProps {
  sectionId: number;
  // The subjects the logged-in teacher teaches in this section; they can update those
  editableSubjectIds?: number[];
}

const STATUS_LABELS: Record<ProgressStatus, string> = {
  not_started: 'Not started',
  in_progress: 'In progress',
  done: 'Done',
};

const STATUS_COLOURS: Record<ProgressStatus, string> = {
  not_started: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-yellow-100 text-yellow-800',
  done: 'bg-green-100 text-green-800',
};

// How much of each subject's syllabus a section has covered.
// Open a subject to see its chapters; its teacher can mark each chapter's progress.
export const ProgressView: React.FC<ProgressViewProps> = ({ sectionId, editableSubjectIds = [] }) => {
  const [subjects, setSubjects] = useState<SectionProgressSubject[]>([]);
  const [loading, setLoading] = useState(true);
  const [openSubjectId, setOpenSubjectId] = useState<number | null>(null);
  const [openSubject, setOpenSubject] = useState<SubjectProgress | null>(null);

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

  const fetchSubject = async (subjectId: number) => {
    try {
      const data = await getSubjectProgress(sectionId, subjectId);
      setOpenSubject(data);
    } catch (error: any) {
      showError(error, 'Failed to load the chapters');
    }
  };

  const toggleSubject = (subjectId: number) => {
    if (openSubjectId === subjectId) {
      setOpenSubjectId(null);
      setOpenSubject(null);
      return;
    }
    setOpenSubjectId(subjectId);
    setOpenSubject(null);
    fetchSubject(subjectId);
  };

  const handleChange = async (chapterId: number, data: { status?: string; planned_date?: string | null }) => {
    if (openSubjectId === null) return;
    try {
      await updateChapterProgress(sectionId, chapterId, data);
      fetchSubject(openSubjectId);
      fetchProgress();
    } catch (error: any) {
      showError(error, 'Failed to update the chapter');
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
        const canEdit = editableSubjectIds.includes(subject.subject_id);
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
                {!openSubject ? (
                  <p className="text-sm text-gray-400">Loading chapters...</p>
                ) : openSubject.chapters.length === 0 ? (
                  <p className="text-sm text-gray-500">The syllabus for this subject has no chapters yet.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="table text-sm">
                      <thead>
                        <tr>
                          <th>Chapter</th>
                          <th>Status</th>
                          <th>Planned by</th>
                          <th>Started</th>
                          <th>Finished</th>
                        </tr>
                      </thead>
                      <tbody>
                        {openSubject.chapters.map((chapter) => (
                          <tr key={chapter.chapter_id}>
                            <td><span className="font-semibold">{chapter.number}.</span> {chapter.title}</td>
                            <td>
                              {canEdit ? (
                                <select value={chapter.status} onChange={(e) => handleChange(chapter.chapter_id, { status: e.target.value })} className="input py-1 text-sm">
                                  <option value="not_started">Not started</option>
                                  <option value="in_progress">In progress</option>
                                  <option value="done">Done</option>
                                </select>
                              ) : (
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLOURS[chapter.status]}`}>{STATUS_LABELS[chapter.status]}</span>
                              )}
                            </td>
                            <td>
                              {canEdit ? (
                                <input type="date" value={chapter.planned_date || ''} onChange={(e) => handleChange(chapter.chapter_id, { planned_date: e.target.value || null })} className="input py-1 text-sm" />
                              ) : (
                                chapter.planned_date || '-'
                              )}
                            </td>
                            <td>{chapter.started_on || '-'}</td>
                            <td>{chapter.completed_on || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
