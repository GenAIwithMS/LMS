import React, { useState } from 'react';
import { X, CheckCircle2, XCircle, Clock } from 'lucide-react';
import type { BellPeriod, DraftSection, TeacherSkills, TimetableSlot } from '../types';

interface PeriodPickerProps {
  day: number;
  dayName: string;
  period: BellPeriod;
  section: DraftSection;          // the section being edited
  sections: DraftSection[];       // every section, to see who is busy where
  teachers: TeacherSkills[];      // every teacher with the subjects they teach
  onChoose: (subjectId: number, teacherId: number | null) => void;
  onClear: () => void;
  onClose: () => void;
}

// What a busy teacher is doing at this time
interface BusyInfo {
  sectionName: string;
  subjectName: string;
}

// True if the teacher's list of subjects has this subject (capitals and spaces don't matter)
const teachesSubject = (teacher: TeacherSkills, subjectName: string): boolean => {
  for (const name of teacher.subjects) {
    if (name.trim().toLowerCase() === subjectName.trim().toLowerCase()) {
      return true;
    }
  }
  return false;
};

// The panel next to the timetable for one period: first the subject, then the teacher.
// Every teacher is shown once, as free or busy, and a busy teacher says exactly where
// and what they are teaching at this time.
export const PeriodPicker: React.FC<PeriodPickerProps> = ({ day, dayName, period, section, sections, teachers, onChoose, onClear, onClose }) => {
  const periodNumber = period.number as number;
  const timeText = `${period.start_time}–${period.end_time}`;

  const currentSlot: TimetableSlot | undefined = section.slots.find((slot) => slot.day === day && slot.period === periodNumber);
  const [subjectId, setSubjectId] = useState<number | null>(currentSlot ? currentSlot.subject_id : null);

  // Who is teaching in the other sections at this time
  const busy: Record<number, BusyInfo> = {};
  const otherSections: { sectionName: string; slot: TimetableSlot | undefined }[] = [];
  for (const other of sections) {
    if (other.section_id === section.section_id) continue;
    const slot = other.slots.find((one) => one.day === day && one.period === periodNumber);
    otherSections.push({ sectionName: other.section_name, slot: slot });
    if (slot && slot.teacher_id !== null) {
      busy[slot.teacher_id] = { sectionName: other.section_name, subjectName: slot.subject_name };
    }
  }

  const busyText = (teacherId: number): string | null => {
    const info = busy[teacherId];
    if (!info) return null;
    return `${info.subjectName} in ${info.sectionName} (${timeText})`;
  };

  const chosenSubject = section.subjects.find((subject) => subject.subject_id === subjectId);

  // The teachers of the chosen subject: the section's own teacher first, then everyone else who teaches it
  const candidates: { teacherId: number; teacherName: string; isCurrent: boolean }[] = [];
  if (chosenSubject) {
    if (chosenSubject.teacher_id !== null && chosenSubject.teacher_name !== null) {
      candidates.push({ teacherId: chosenSubject.teacher_id, teacherName: chosenSubject.teacher_name, isCurrent: true });
    }
    for (const teacher of teachers) {
      if (teacher.teacher_id !== chosenSubject.teacher_id && teachesSubject(teacher, chosenSubject.subject_name)) {
        candidates.push({ teacherId: teacher.teacher_id, teacherName: teacher.teacher_name, isCurrent: false });
      }
    }
  }

  // Everyone once, free first, with what they could teach in this class
  const everyone: { teacher: TeacherSkills; busyText: string | null; canTeachHere: string[] }[] = [];
  for (const teacher of teachers) {
    const canTeachHere: string[] = [];
    for (const subject of section.subjects) {
      if (subject.teacher_id === teacher.teacher_id || teachesSubject(teacher, subject.subject_name)) {
        canTeachHere.push(subject.subject_name);
      }
    }
    everyone.push({ teacher: teacher, busyText: busyText(teacher.teacher_id), canTeachHere: canTeachHere });
  }
  everyone.sort((first, second) => {
    if (first.busyText === null && second.busyText !== null) return -1;
    if (first.busyText !== null && second.busyText === null) return 1;
    return first.teacher.teacher_name.localeCompare(second.teacher.teacher_name);
  });

  return (
    <div className="card space-y-5 text-sm">
      {/* Which period */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-lg font-bold text-gray-900">{dayName}, Period {periodNumber}</div>
          <div className="text-gray-500 flex items-center gap-1"><Clock size={14} /> {timeText} · {section.section_name}</div>
        </div>
        <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-700" title="Close"><X size={18} /></button>
      </div>

      <div className="flex items-center justify-between gap-2 p-3 rounded-lg bg-gray-50">
        <div>
          <span className="text-gray-500">Now: </span>
          {currentSlot ? (
            <span className="font-semibold">{currentSlot.subject_name} – {currentSlot.teacher_name || 'no teacher yet'}</span>
          ) : (
            <span className="font-semibold">Free</span>
          )}
        </div>
        {currentSlot && (
          <button onClick={onClear} className="btn btn-secondary text-xs">Make it free</button>
        )}
      </div>

      {/* Step 1: the subject */}
      <div>
        <div className="font-semibold text-gray-800 mb-2">1. Subject</div>
        {section.subjects.length === 0 ? (
          <p className="text-gray-500">This class has no subjects yet.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {section.subjects.map((subject) => (
              <button
                key={subject.subject_id}
                onClick={() => setSubjectId(subject.subject_id)}
                className={`px-3 py-1 rounded-lg border text-sm ${subject.subject_id === subjectId ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300 hover:border-primary-400'}`}
              >
                {subject.subject_name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Step 2: the teacher for that subject */}
      {chosenSubject && (
        <div>
          <div className="font-semibold text-gray-800 mb-2">2. Teacher for {chosenSubject.subject_name}</div>
          {candidates.length === 0 ? (
            <div className="space-y-2">
              <p className="text-gray-500">No teacher has {chosenSubject.subject_name} in their subjects yet. Add it to a teacher on the Teachers page.</p>
              <button onClick={() => onChoose(chosenSubject.subject_id, null)} className="btn btn-secondary text-xs">Put {chosenSubject.subject_name} here without a teacher</button>
            </div>
          ) : (
            <div className="space-y-2">
              {candidates.map((candidate) => {
                const isThisPeriodsChoice = currentSlot !== undefined && currentSlot.subject_id === chosenSubject.subject_id && currentSlot.teacher_id === candidate.teacherId;
                const reason = busyText(candidate.teacherId);
                return (
                  <div key={candidate.teacherId} className={`flex items-center justify-between gap-2 p-2 rounded-lg border ${reason ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}`}>
                    <div>
                      <div className="font-semibold text-gray-900">{candidate.teacherName}</div>
                      {reason ? (
                        <div className="text-xs text-red-700 flex items-center gap-1"><XCircle size={12} /> Busy: {reason}</div>
                      ) : isThisPeriodsChoice ? (
                        <div className="text-xs text-primary-700 flex items-center gap-1"><CheckCircle2 size={12} /> Teaching this period</div>
                      ) : (
                        <div className="text-xs text-green-700 flex items-center gap-1"><CheckCircle2 size={12} /> Free at this time</div>
                      )}
                      {candidate.isCurrent && (
                        <div className="text-xs text-gray-500">Teaches {chosenSubject.subject_name} in {section.section_name}</div>
                      )}
                      {!candidate.isCurrent && chosenSubject.teacher_id !== null && (
                        <div className="text-xs text-gray-500">Choosing them makes them {section.section_name}'s {chosenSubject.subject_name} teacher (all its periods)</div>
                      )}
                    </div>
                    {isThisPeriodsChoice ? (
                      <span className="text-xs font-semibold text-primary-700">Chosen</span>
                    ) : (
                      <button onClick={() => onChoose(chosenSubject.subject_id, candidate.teacherId)} disabled={reason !== null} className="btn btn-primary text-xs px-3 py-1 disabled:opacity-40 disabled:cursor-not-allowed">Choose</button>
                    )}
                  </div>
                );
              })}
              {chosenSubject.teacher_id === null && (
                <button onClick={() => onChoose(chosenSubject.subject_id, null)} className="text-xs text-gray-500 hover:underline">Or put {chosenSubject.subject_name} here without a teacher</button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Everyone's availability at this time */}
      <div>
        <div className="font-semibold text-gray-800 mb-2">Who's free at {timeText}</div>
        <div className="space-y-1">
          {everyone.map((row) => (
            <div key={row.teacher.teacher_id} className="flex items-start justify-between gap-2">
              <span className="font-medium text-gray-800">{row.teacher.teacher_name}</span>
              {row.busyText ? (
                <span className="text-xs text-red-700 text-right">Busy: {row.busyText}</span>
              ) : currentSlot !== undefined && currentSlot.teacher_id === row.teacher.teacher_id ? (
                // The teacher of the period being edited: not "Free", they teach it
                <span className="text-xs text-primary-700 font-semibold text-right">Teaching this period ({currentSlot.subject_name})</span>
              ) : (
                <span className="text-xs text-green-700 text-right">
                  Free{row.canTeachHere.length > 0 ? ` · can teach ${row.canTeachHere.join(', ')}` : ' · no subject of this class'}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* The other sections in this period */}
      {otherSections.length > 0 && (
        <div>
          <div className="font-semibold text-gray-800 mb-2">Other sections at {timeText}</div>
          <div className="space-y-1">
            {otherSections.map((row) => (
              <div key={row.sectionName} className="flex justify-between gap-2">
                <span className="text-gray-700">{row.sectionName}</span>
                <span className="text-xs text-gray-600 text-right">
                  {row.slot ? `${row.slot.subject_name} – ${row.slot.teacher_name || 'no teacher yet'}` : 'Free'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
