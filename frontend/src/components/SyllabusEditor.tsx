import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUp, ArrowDown, Edit, Trash2, Check, Plus } from 'lucide-react';
import {
  getSubjectProgress, addSectionChapter, updateChapter, deleteChapter, moveChapter, updateChapterProgress,
  addTopic, updateTopic, deleteTopic, moveTopic, setTopicDone, getSectionDiary, saveDiaryEntry,
} from '../services/api';
import type { SubjectProgress, ChapterProgressItem, SyllabusTopicItem, ProgressStatus, DiaryEntry } from '../types';
import { Modal } from './Modal';
import { showError, showSuccess } from '../utils/errorHandler';

// One subject's syllabus in one section: chapters, each with daily topics.
// The teacher who teaches the subject there writes it and ticks topics off; from a done
// topic they can set an assignment, a class test or today's diary. Everyone else
// (the admin, the section's students) sees it read-only.

interface SyllabusEditorProps {
  sectionId: number;
  subjectId: number;
  onChanged?: () => void;
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

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// "2026-11-12" -> "12 Nov 2026" (read from the text, so no time zone moves the day)
const readableDate = (value: string | null | undefined, withYear = true): string => {
  if (!value) {
    return '';
  }
  const parts = value.slice(0, 10).split('-');
  if (parts.length !== 3) {
    return value;
  }
  const text = `${Number(parts[2])} ${MONTHS[Number(parts[1]) - 1]}`;
  return withYear ? `${text} ${parts[0]}` : text;
};

const todayText = () => new Date().toLocaleDateString('en-CA');

export const SyllabusEditor: React.FC<SyllabusEditorProps> = ({ sectionId, subjectId, onChanged }) => {
  const navigate = useNavigate();
  const [syllabus, setSyllabus] = useState<SubjectProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [newChapterTitle, setNewChapterTitle] = useState('');

  // Confirm windows
  const [chapterToDelete, setChapterToDelete] = useState<ChapterProgressItem | null>(null);
  const [topicToDelete, setTopicToDelete] = useState<SyllabusTopicItem | null>(null);

  // Today's diary window, written from a topic
  const [diaryTopic, setDiaryTopic] = useState<SyllabusTopicItem | null>(null);
  const [classwork, setClasswork] = useState('');
  const [homework, setHomework] = useState('');

  useEffect(() => {
    fetchSyllabus();
  }, [sectionId, subjectId]);

  const fetchSyllabus = async () => {
    try {
      const data = await getSubjectProgress(sectionId, subjectId);
      setSyllabus(data);
    } catch (error: any) {
      showError(error, 'Failed to load the syllabus');
    } finally {
      setLoading(false);
    }
  };

  // Run a change, show the server's message, then reload
  const change = async (work: () => Promise<any>, failText: string, quiet = false) => {
    try {
      const data = await work();
      if (!quiet && data && data.message) {
        showSuccess(data.message);
      }
      await fetchSyllabus();
      if (onChanged) {
        onChanged();
      }
      return true;
    } catch (error: any) {
      showError(error, failText);
      return false;
    }
  };

  const handleAddChapter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChapterTitle.trim()) return;
    const ok = await change(() => addSectionChapter(sectionId, subjectId, { title: newChapterTitle.trim() }), 'Failed to add the chapter');
    if (ok) {
      setNewChapterTitle('');
    }
  };

  const confirmDeleteChapter = async () => {
    if (!chapterToDelete) return;
    await change(() => deleteChapter(chapterToDelete.chapter_id), 'Failed to delete the chapter');
    setChapterToDelete(null);
  };

  const confirmDeleteTopic = async () => {
    if (!topicToDelete) return;
    await change(() => deleteTopic(topicToDelete.topic_id), 'Failed to delete the topic');
    setTopicToDelete(null);
  };

  // Open today's diary for this subject, with the topic added to the classwork
  const openDiary = async (topic: SyllabusTopicItem) => {
    let existing: DiaryEntry | undefined;
    try {
      const data = await getSectionDiary(sectionId, todayText());
      const entries: DiaryEntry[] = Array.isArray(data.entries) ? data.entries : [];
      existing = entries.find((entry) => entry.subject_id === subjectId);
    } catch (error) {
      existing = undefined;
    }
    if (existing && existing.classwork) {
      setClasswork(existing.classwork + '\n' + topic.title);
    } else {
      setClasswork(topic.title);
    }
    setHomework(existing && existing.homework ? existing.homework : '');
    setDiaryTopic(topic);
  };

  const handleSaveDiary = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!diaryTopic) return;
    const topicId = diaryTopic.topic_id;
    const ok = await change(
      () => saveDiaryEntry(sectionId, { subject_id: subjectId, date: todayText(), classwork, homework, topic_id: topicId }),
      'Failed to save the diary'
    );
    if (ok) {
      setDiaryTopic(null);
    }
  };

  if (loading) {
    return <p className="text-sm text-gray-400">Loading the syllabus...</p>;
  }
  if (!syllabus) {
    return <p className="text-sm text-red-500">Could not load the syllabus.</p>;
  }

  const canEdit = syllabus.can_edit;

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-600">
        {syllabus.chapter_count} {syllabus.chapter_count === 1 ? 'chapter' : 'chapters'}
        {syllabus.topic_count > 0 && ` · ${syllabus.topics_done} of ${syllabus.topic_count} topics done`}
        {` · ${syllabus.percentage}% covered`}
      </p>

      {syllabus.chapters.length === 0 && (
        <p className="text-sm text-gray-500">
          {canEdit ? 'No chapters yet. Add the first chapter below.' : "The teacher hasn't added the syllabus yet."}
        </p>
      )}

      {syllabus.chapters.map((chapter, index) => (
        <ChapterBlock
          key={chapter.chapter_id}
          chapter={chapter}
          isFirst={index === 0}
          isLast={index === syllabus.chapters.length - 1}
          canEdit={canEdit}
          sectionId={sectionId}
          change={change}
          onDelete={() => setChapterToDelete(chapter)}
          onDeleteTopic={(topic) => setTopicToDelete(topic)}
          onAssignment={(topic) => navigate(`/teacher/assignments?new=1&section=${sectionId}&subject=${subjectId}&topic=${topic.topic_id}&topicTitle=${encodeURIComponent(topic.title)}`)}
          onClassTest={(topic) => navigate(`/teacher/class-tests?new=1&section=${sectionId}&subject=${subjectId}&chapter=${chapter.chapter_id}&topic=${topic.topic_id}&topicTitle=${encodeURIComponent(topic.title)}`)}
          onDiary={openDiary}
        />
      ))}

      {canEdit && (
        <form onSubmit={handleAddChapter} className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={newChapterTitle}
            onChange={(e) => setNewChapterTitle(e.target.value)}
            placeholder="New chapter, e.g. Fractions"
            className="input flex-1"
          />
          <button type="submit" className="btn btn-primary flex items-center justify-center gap-1">
            <Plus size={16} /> Add chapter
          </button>
        </form>
      )}

      <Modal isOpen={chapterToDelete !== null} onClose={() => setChapterToDelete(null)} title="Delete chapter">
        {chapterToDelete && (
          <div className="space-y-4">
            <p className="text-sm text-gray-700">
              Delete chapter {chapterToDelete.number}: {chapterToDelete.title}? Its topics and progress are deleted too. Assignments and tests made from it stay.
            </p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setChapterToDelete(null)} className="btn btn-secondary">Cancel</button>
              <button onClick={confirmDeleteChapter} className="btn bg-red-600 text-white hover:bg-red-700">Delete</button>
            </div>
          </div>
        )}
      </Modal>

      <Modal isOpen={topicToDelete !== null} onClose={() => setTopicToDelete(null)} title="Delete topic">
        {topicToDelete && (
          <div className="space-y-4">
            <p className="text-sm text-gray-700">Delete topic: {topicToDelete.title}? Anything made from it stays.</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setTopicToDelete(null)} className="btn btn-secondary">Cancel</button>
              <button onClick={confirmDeleteTopic} className="btn bg-red-600 text-white hover:bg-red-700">Delete</button>
            </div>
          </div>
        )}
      </Modal>

      <Modal isOpen={diaryTopic !== null} onClose={() => setDiaryTopic(null)} title={diaryTopic ? `Today's diary: ${diaryTopic.title}` : "Today's diary"}>
        <form onSubmit={handleSaveDiary} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Classwork (what was taught)</label>
            <textarea value={classwork} onChange={(e) => setClasswork(e.target.value)} rows={4} className="input w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Homework</label>
            <textarea value={homework} onChange={(e) => setHomework(e.target.value)} rows={3} className="input w-full" />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setDiaryTopic(null)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

// ---------------- One chapter with its topics

interface ChapterBlockProps {
  chapter: ChapterProgressItem;
  isFirst: boolean;
  isLast: boolean;
  canEdit: boolean;
  sectionId: number;
  change: (work: () => Promise<any>, failText: string, quiet?: boolean) => Promise<boolean>;
  onDelete: () => void;
  onDeleteTopic: (topic: SyllabusTopicItem) => void;
  onAssignment: (topic: SyllabusTopicItem) => void;
  onClassTest: (topic: SyllabusTopicItem) => void;
  onDiary: (topic: SyllabusTopicItem) => void;
}

const ChapterBlock: React.FC<ChapterBlockProps> = ({
  chapter, isFirst, isLast, canEdit, sectionId, change, onDelete, onDeleteTopic, onAssignment, onClassTest, onDiary,
}) => {
  const [renaming, setRenaming] = useState(false);
  const [title, setTitle] = useState(chapter.title);
  const [newTopicTitle, setNewTopicTitle] = useState('');
  const [newTopicDate, setNewTopicDate] = useState('');
  const hasTopics = chapter.topics.length > 0;
  const label = `chapter ${chapter.number}: ${chapter.title}`;

  const saveTitle = async () => {
    if (!title.trim()) return;
    const ok = await change(() => updateChapter(chapter.chapter_id, { title: title.trim() }), 'Failed to rename the chapter');
    if (ok) {
      setRenaming(false);
    }
  };

  const handleAddTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTopicTitle.trim()) return;
    const ok = await change(
      () => addTopic(chapter.chapter_id, { title: newTopicTitle.trim(), planned_date: newTopicDate || null }),
      'Failed to add the topic'
    );
    if (ok) {
      setNewTopicTitle('');
      setNewTopicDate('');
    }
  };

  return (
    <div className="border border-gray-200 rounded-xl p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        {renaming ? (
          <div className="flex flex-1 items-center gap-2">
            <span className="font-semibold text-gray-900">{chapter.number}.</span>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="input py-1 text-sm flex-1 min-w-0" />
            <button onClick={saveTitle} className="btn btn-primary text-xs px-3 py-1">Save</button>
            <button onClick={() => { setRenaming(false); setTitle(chapter.title); }} className="btn btn-secondary text-xs px-3 py-1">Cancel</button>
          </div>
        ) : (
          <div className="font-semibold text-gray-900">{chapter.number}. {chapter.title}</div>
        )}

        <div className="flex items-center gap-1">
          {canEdit && !hasTopics ? (
            <select
              value={chapter.status}
              onChange={(e) => change(() => updateChapterProgress(sectionId, chapter.chapter_id, { status: e.target.value }), 'Failed to update the chapter', true)}
              className="input py-1 pl-2 pr-8 text-xs w-auto"
              aria-label={`Progress of ${label}`}
            >
              <option value="not_started">Not started</option>
              <option value="in_progress">In progress</option>
              <option value="done">Done</option>
            </select>
          ) : (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLOURS[chapter.status]}`}>{STATUS_LABELS[chapter.status]}</span>
          )}
          {canEdit && !renaming && (
            <>
              <button onClick={() => change(() => moveChapter(chapter.chapter_id, 'up'), 'Failed to move the chapter', true)} disabled={isFirst}
                className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30" title={`Move ${label} up`} aria-label={`Move ${label} up`}>
                <ArrowUp size={15} />
              </button>
              <button onClick={() => change(() => moveChapter(chapter.chapter_id, 'down'), 'Failed to move the chapter', true)} disabled={isLast}
                className="p-1.5 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30" title={`Move ${label} down`} aria-label={`Move ${label} down`}>
                <ArrowDown size={15} />
              </button>
              <button onClick={() => setRenaming(true)} className="p-1.5 text-blue-600 hover:bg-blue-50 rounded" title={`Rename ${label}`} aria-label={`Rename ${label}`}>
                <Edit size={15} />
              </button>
              <button onClick={onDelete} className="p-1.5 text-red-600 hover:bg-red-50 rounded" title={`Delete ${label}`} aria-label={`Delete ${label}`}>
                <Trash2 size={15} />
              </button>
            </>
          )}
        </div>
      </div>
      {hasTopics && <p className="text-xs text-gray-400 mt-1">Progress follows its topics</p>}

      {hasTopics && (
        <ul className="mt-2 space-y-2">
          {chapter.topics.map((topic, index) => (
            <TopicRow
              key={topic.topic_id}
              topic={topic}
              isFirst={index === 0}
              isLast={index === chapter.topics.length - 1}
              canEdit={canEdit}
              change={change}
              onDelete={() => onDeleteTopic(topic)}
              onAssignment={() => onAssignment(topic)}
              onClassTest={() => onClassTest(topic)}
              onDiary={() => onDiary(topic)}
            />
          ))}
        </ul>
      )}

      {canEdit && (
        <form onSubmit={handleAddTopic} className="mt-2 flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={newTopicTitle}
            onChange={(e) => setNewTopicTitle(e.target.value)}
            placeholder="New daily topic"
            className="input py-1 text-sm flex-1 min-w-0"
          />
          <input
            type="date"
            value={newTopicDate}
            onChange={(e) => setNewTopicDate(e.target.value)}
            className="input py-1 text-sm sm:w-44 sm:flex-none"
            title="Planned day (optional)"
            aria-label="Planned day (optional)"
          />
          <button type="submit" className="btn btn-secondary text-sm px-3 py-1 flex items-center justify-center gap-1 whitespace-nowrap shrink-0">
            <Plus size={14} /> Add topic
          </button>
        </form>
      )}
    </div>
  );
};

// ---------------- One daily topic

interface TopicRowProps {
  topic: SyllabusTopicItem;
  isFirst: boolean;
  isLast: boolean;
  canEdit: boolean;
  change: (work: () => Promise<any>, failText: string, quiet?: boolean) => Promise<boolean>;
  onDelete: () => void;
  onAssignment: () => void;
  onClassTest: () => void;
  onDiary: () => void;
}

const TopicRow: React.FC<TopicRowProps> = ({ topic, isFirst, isLast, canEdit, change, onDelete, onAssignment, onClassTest, onDiary }) => {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(topic.title);
  const [plannedDate, setPlannedDate] = useState(topic.planned_date || '');
  const label = `topic ${topic.title}`;

  const saveTopic = async () => {
    if (!title.trim()) return;
    const ok = await change(() => updateTopic(topic.topic_id, { title: title.trim(), planned_date: plannedDate || null }), 'Failed to change the topic');
    if (ok) {
      setEditing(false);
    }
  };

  const links = topic.links;
  const hasLinks = links.assignments.length > 0 || links.class_tests.length > 0 || links.diary.length > 0;

  return (
    <li className="pl-2 border-l-2 border-gray-100">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          {canEdit ? (
            <input
              type="checkbox"
              checked={topic.is_done}
              onChange={(e) => change(() => setTopicDone(topic.topic_id, e.target.checked), 'Failed to update the topic', true)}
              className="mt-1"
              aria-label={`Done: ${topic.title}`}
            />
          ) : (
            <span className={`mt-0.5 ${topic.is_done ? 'text-green-600' : 'text-gray-300'}`}><Check size={16} /></span>
          )}
          {editing ? (
            <div className="flex flex-1 flex-col sm:flex-row gap-2">
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="input py-1 text-sm flex-1" />
              <input type="date" value={plannedDate} onChange={(e) => setPlannedDate(e.target.value)} className="input py-1 text-sm sm:w-44 sm:flex-none" aria-label="Planned day" />
              <button onClick={saveTopic} className="btn btn-primary text-xs px-3 py-1">Save</button>
              <button onClick={() => { setEditing(false); setTitle(topic.title); setPlannedDate(topic.planned_date || ''); }} className="btn btn-secondary text-xs px-3 py-1">Cancel</button>
            </div>
          ) : (
            <div className="min-w-0">
              <div className={`text-sm ${topic.is_done ? 'text-gray-500 line-through' : 'text-gray-800'}`}>{topic.number}. {topic.title}</div>
              <div className="text-xs text-gray-400">
                {topic.planned_date && `Planned ${readableDate(topic.planned_date)}`}
                {topic.planned_date && topic.is_done && ' · '}
                {topic.is_done && topic.done_on && `Done on ${readableDate(topic.done_on)}`}
              </div>
            </div>
          )}
        </div>

        {canEdit && !editing && (
          <div className="flex items-center gap-1">
            <button onClick={() => change(() => moveTopic(topic.topic_id, 'up'), 'Failed to move the topic', true)} disabled={isFirst}
              className="p-1 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30" title={`Move ${label} up`} aria-label={`Move ${label} up`}>
              <ArrowUp size={14} />
            </button>
            <button onClick={() => change(() => moveTopic(topic.topic_id, 'down'), 'Failed to move the topic', true)} disabled={isLast}
              className="p-1 text-gray-500 hover:bg-gray-100 rounded disabled:opacity-30" title={`Move ${label} down`} aria-label={`Move ${label} down`}>
              <ArrowDown size={14} />
            </button>
            <button onClick={() => setEditing(true)} className="p-1 text-blue-600 hover:bg-blue-50 rounded" title={`Edit ${label}`} aria-label={`Edit ${label}`}>
              <Edit size={14} />
            </button>
            <button onClick={onDelete} className="p-1 text-red-600 hover:bg-red-50 rounded" title={`Delete ${label}`} aria-label={`Delete ${label}`}>
              <Trash2 size={14} />
            </button>
          </div>
        )}
      </div>

      {/* From a topic that has been taught: set work on it */}
      {canEdit && topic.is_done && !editing && (
        <div className="flex flex-wrap gap-2 mt-1 ml-6">
          <button onClick={onAssignment} className="text-xs px-2 py-1 rounded bg-primary-50 text-primary-700 hover:bg-primary-100">+ Assignment</button>
          <button onClick={onClassTest} className="text-xs px-2 py-1 rounded bg-primary-50 text-primary-700 hover:bg-primary-100">+ Class test</button>
          <button onClick={onDiary} className="text-xs px-2 py-1 rounded bg-primary-50 text-primary-700 hover:bg-primary-100">+ Diary</button>
        </div>
      )}

      {/* What was made from this topic */}
      {hasLinks && (
        <div className="ml-6 mt-1 space-y-0.5">
          {links.assignments.map((item) => (
            <div key={`a-${item.id}`} className="text-xs text-gray-500">Assignment: {item.title} (due {readableDate(item.due_date, false)})</div>
          ))}
          {links.class_tests.map((item) => (
            <div key={`t-${item.id}`} className="text-xs text-gray-500">Class test: {item.title} ({readableDate(item.date, false)})</div>
          ))}
          {links.diary.map((item) => (
            <div key={`d-${item.id}`} className="text-xs text-gray-500">Diary: {readableDate(item.date, false)}</div>
          ))}
        </div>
      )}
    </li>
  );
};
