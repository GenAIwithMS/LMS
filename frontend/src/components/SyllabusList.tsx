import React, { useState, useEffect } from 'react';
import { Check } from 'lucide-react';
import { getSectionChapters } from '../services/api';
import type { SyllabusChapter } from '../types';

interface SyllabusListProps {
  sectionId: number;
  subjectId: number;
}

// One subject's syllabus in a section, read-only: chapters with their daily topics
// (topics already taught are ticked).
export const SyllabusList: React.FC<SyllabusListProps> = ({ sectionId, subjectId }) => {
  const [chapters, setChapters] = useState<SyllabusChapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const fetchChapters = async () => {
      try {
        setLoading(true);
        const data = await getSectionChapters(sectionId, subjectId);
        setChapters(Array.isArray(data.data) ? data.data : []);
        setFailed(false);
      } catch (error) {
        setFailed(true);
      } finally {
        setLoading(false);
      }
    };
    fetchChapters();
  }, [sectionId, subjectId]);

  if (loading) {
    return <p className="text-sm text-gray-400">Loading chapters...</p>;
  }
  if (failed) {
    return <p className="text-sm text-red-500">Could not load the chapters.</p>;
  }
  if (chapters.length === 0) {
    return <p className="text-sm text-gray-500">The teacher hasn't added the syllabus yet.</p>;
  }

  return (
    <ol className="space-y-2">
      {chapters.map((chapter) => (
        <li key={chapter.id} className="text-sm text-gray-700">
          <span className="font-semibold">{chapter.number}.</span> {chapter.title}
          {chapter.topics && chapter.topics.length > 0 && (
            <ul className="mt-1 ml-5 space-y-0.5">
              {chapter.topics.map((topic) => (
                <li key={topic.id} className={`flex items-center gap-1 text-xs ${topic.is_done ? 'text-gray-500' : 'text-gray-700'}`}>
                  <span className={topic.is_done ? 'text-green-600' : 'text-gray-300'}><Check size={12} /></span>
                  {topic.title}
                </li>
              ))}
            </ul>
          )}
        </li>
      ))}
    </ol>
  );
};
