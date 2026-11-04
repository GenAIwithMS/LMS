import React, { useState, useEffect } from 'react';
import { getSubjectChapters } from '../services/api';
import type { SyllabusChapter } from '../types';

interface SyllabusListProps {
  subjectId: number;
}

// The chapters of one subject's syllabus, read-only (for teachers and students).
export const SyllabusList: React.FC<SyllabusListProps> = ({ subjectId }) => {
  const [chapters, setChapters] = useState<SyllabusChapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const fetchChapters = async () => {
      try {
        setLoading(true);
        const data = await getSubjectChapters(subjectId);
        setChapters(Array.isArray(data.data) ? data.data : []);
        setFailed(false);
      } catch (error) {
        setFailed(true);
      } finally {
        setLoading(false);
      }
    };
    fetchChapters();
  }, [subjectId]);

  if (loading) {
    return <p className="text-sm text-gray-400">Loading chapters...</p>;
  }
  if (failed) {
    return <p className="text-sm text-red-500">Could not load the chapters.</p>;
  }
  if (chapters.length === 0) {
    return <p className="text-sm text-gray-500">The syllabus for this subject has no chapters yet.</p>;
  }

  return (
    <ol className="space-y-1">
      {chapters.map((chapter) => (
        <li key={chapter.id} className="text-sm text-gray-700">
          <span className="font-semibold">{chapter.number}.</span> {chapter.title}
        </li>
      ))}
    </ol>
  );
};
