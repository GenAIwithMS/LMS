import React, { useState, useEffect } from 'react';
import { PenSquare, Trash2, Edit } from 'lucide-react';
import { getSectionDiary, saveDiaryEntry, deleteDiaryEntry } from '../services/api';
import type { DiaryEntry } from '../types';
import { Modal } from './Modal';
import { showError, showSuccess } from '../utils/errorHandler';
import { todayText } from '../utils/date';

interface DiaryViewProps {
  sectionId: number;
  // The subjects the logged-in teacher teaches in this section (empty for everyone else)
  writableSubjects?: { subject_id: number; subject_name: string }[];
}

// A section's daily diary: what was taught in each subject on a day, and the homework.
// Everyone who can open the section can read it. Subject teachers write their own subject.
export const DiaryView: React.FC<DiaryViewProps> = ({ sectionId, writableSubjects = [] }) => {
  const [date, setDate] = useState(todayText());
  const [entries, setEntries] = useState<DiaryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  // The write window
  const [editingSubject, setEditingSubject] = useState<{ subject_id: number; subject_name: string } | null>(null);
  const [classwork, setClasswork] = useState('');
  const [homework, setHomework] = useState('');

  const [entryToDelete, setEntryToDelete] = useState<DiaryEntry | null>(null);

  useEffect(() => {
    fetchDiary();
  }, [sectionId, date]);

  const fetchDiary = async () => {
    try {
      const data = await getSectionDiary(sectionId, date);
      setEntries(Array.isArray(data.entries) ? data.entries : []);
    } catch (error: any) {
      showError(error, 'Failed to load the diary');
    } finally {
      setLoading(false);
    }
  };

  const findEntry = (subjectId: number): DiaryEntry | undefined => {
    return entries.find((entry) => entry.subject_id === subjectId);
  };

  const openWrite = (subject: { subject_id: number; subject_name: string }) => {
    const existing = findEntry(subject.subject_id);
    setClasswork(existing && existing.classwork ? existing.classwork : '');
    setHomework(existing && existing.homework ? existing.homework : '');
    setEditingSubject(subject);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingSubject) return;
    try {
      const data = await saveDiaryEntry(sectionId, {
        subject_id: editingSubject.subject_id,
        date: date,
        classwork: classwork.trim(),
        homework: homework.trim(),
      });
      showSuccess(data.message || 'Diary saved');
      setEditingSubject(null);
      fetchDiary();
    } catch (error: any) {
      showError(error, 'Failed to save the diary');
    }
  };

  const handleDelete = async () => {
    if (!entryToDelete) return;
    try {
      await deleteDiaryEntry(entryToDelete.id);
      showSuccess('Diary entry deleted');
      setEntryToDelete(null);
      fetchDiary();
    } catch (error: any) {
      showError(error, 'Failed to delete the diary entry');
    }
  };

  const canWrite = (subjectId: number): boolean => {
    return writableSubjects.some((subject) => subject.subject_id === subjectId);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-gray-600">Day</label>
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="input max-w-[12rem]" />
        {writableSubjects.map((subject) => (
          <button key={subject.subject_id} onClick={() => openWrite(subject)} className="btn btn-primary text-sm flex items-center gap-1">
            <PenSquare size={14} /> {findEntry(subject.subject_id) ? 'Edit' : 'Write'} {subject.subject_name}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-gray-400">Loading the diary...</p>
      ) : entries.length === 0 ? (
        <p className="text-sm text-gray-500">Nothing in the diary for this day.</p>
      ) : (
        <div className="space-y-3">
          {entries.map((entry) => (
            <div key={entry.id} className="border border-gray-200 rounded-xl p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold text-gray-900">{entry.subject_name}</div>
                  <div className="text-xs text-gray-500">{entry.teacher_name}</div>
                </div>
                {canWrite(entry.subject_id) && (
                  <div className="flex">
                    <button onClick={() => openWrite({ subject_id: entry.subject_id, subject_name: entry.subject_name })} className="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Edit"><Edit size={14} /></button>
                    <button onClick={() => setEntryToDelete(entry)} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Delete"><Trash2 size={14} /></button>
                  </div>
                )}
              </div>
              {entry.classwork && (
                <div className="mt-2 text-sm"><span className="font-semibold text-gray-700">Classwork: </span>{entry.classwork}</div>
              )}
              {entry.homework && (
                <div className="mt-1 text-sm"><span className="font-semibold text-gray-700">Homework: </span>{entry.homework}</div>
              )}
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={editingSubject !== null} onClose={() => setEditingSubject(null)} title={editingSubject ? `${editingSubject.subject_name} diary for ${date}` : ''}>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Classwork (what was taught)</label>
            <textarea value={classwork} onChange={(e) => setClasswork(e.target.value)} rows={3} className="input" placeholder="e.g. Fractions, page 12-13" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Homework</label>
            <textarea value={homework} onChange={(e) => setHomework(e.target.value)} rows={3} className="input" placeholder="e.g. Exercise 2.1, questions 1-5" />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setEditingSubject(null)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">Save</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={entryToDelete !== null} onClose={() => setEntryToDelete(null)} title="Delete diary entry">
        <p className="text-sm text-gray-700">Delete the {entryToDelete?.subject_name} diary for {entryToDelete?.date}?</p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setEntryToDelete(null)} className="btn btn-secondary">Cancel</button>
          <button onClick={handleDelete} className="btn btn-primary bg-red-600 hover:bg-red-700">Delete</button>
        </div>
      </Modal>
    </div>
  );
};
