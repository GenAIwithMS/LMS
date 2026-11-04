import React from 'react';
import type { BellPeriod, PeriodSubject, TimetableSlot, TeacherSkills } from '../types';

interface TimetableGridProps {
  timetable: {
    days: { day: number; name: string }[];
    periods: BellPeriod[];
    slots: TimetableSlot[];
  };
  // A teacher's own week shows the section of each period instead of the teacher
  showSection?: boolean;
  // Give this to let the admin choose the subject of each period
  edit?: {
    // The section's subjects, each with its current teacher in this section
    subjects: PeriodSubject[];
    // Every teacher with the subjects they teach, so other free teachers of a subject can be offered
    teachers: TeacherSkills[];
    // Where this teacher already is at this time (another section's name), or null when free
    busyIn: (day: number, period: number, teacherId: number) => string | null;
    onChange: (day: number, period: number, subjectId: number | null, teacherId: number | null) => void;
  };
}

// Soft colours so each subject is easy to spot across the week
const SUBJECT_COLOURS = [
  'bg-blue-50 border-blue-200',
  'bg-green-50 border-green-200',
  'bg-yellow-50 border-yellow-200',
  'bg-purple-50 border-purple-200',
  'bg-pink-50 border-pink-200',
  'bg-orange-50 border-orange-200',
  'bg-teal-50 border-teal-200',
  'bg-indigo-50 border-indigo-200',
  'bg-lime-50 border-lime-200',
  'bg-rose-50 border-rose-200',
];

const subjectColour = (subjectId: number | null): string => {
  if (subjectId === null) {
    return 'bg-gray-50 border-gray-200';
  }
  return SUBJECT_COLOURS[subjectId % SUBJECT_COLOURS.length];
};

// True if the teacher's list of subjects has this subject (capitals and spaces don't matter)
const teachesSubject = (teacher: TeacherSkills, subjectName: string): boolean => {
  for (const name of teacher.subjects) {
    if (name.trim().toLowerCase() === subjectName.trim().toLowerCase()) {
      return true;
    }
  }
  return false;
};

// The weekly timetable like a college timetable: days down the side, the periods
// (with their times) across the top, and breaks as a shaded column.
export const TimetableGrid: React.FC<TimetableGridProps> = ({ timetable, showSection, edit }) => {
  const findSlot = (day: number, period: number): TimetableSlot | undefined => {
    return timetable.slots.find((slot) => slot.day === day && slot.period === period);
  };

  // A choice in a period is "subject:teacher", or "subject:none" for a subject with no teacher yet
  const choiceValue = (subjectId: number, teacherId: number | null): string => {
    if (teacherId === null) {
      return `${subjectId}:none`;
    }
    return `${subjectId}:${teacherId}`;
  };

  const handleChoice = (day: number, period: number, value: string) => {
    if (!edit) return;
    if (value === '') {
      edit.onChange(day, period, null, null);
      return;
    }
    const parts = value.split(':');
    const subjectId = Number(parts[0]);
    let teacherId: number | null = null;
    if (parts[1] !== 'none') {
      teacherId = Number(parts[1]);
    }
    edit.onChange(day, period, subjectId, teacherId);
  };

  const renderEditCell = (day: number, period: number) => {
    if (!edit) return null;
    const slot = findSlot(day, period);
    let currentValue = '';
    if (slot) {
      currentValue = choiceValue(slot.subject_id, slot.teacher_id);
    }
    return (
      <div className={`rounded-lg border p-1 ${slot ? subjectColour(slot.subject_id) : 'border-dashed border-gray-300'}`}>
        <select
          value={currentValue}
          onChange={(e) => handleChoice(day, period, e.target.value)}
          className="w-full bg-transparent text-xs font-semibold text-gray-900 focus:outline-none cursor-pointer"
          title="Choose the subject and teacher for this period"
        >
          <option value="">Free</option>
          {edit.subjects.map((subject) => {
            // The section's own teacher of the subject first, then every other teacher who teaches it
            const candidates: { teacherId: number; teacherName: string; isCurrent: boolean }[] = [];
            if (subject.teacher_id !== null && subject.teacher_name !== null) {
              candidates.push({ teacherId: subject.teacher_id, teacherName: subject.teacher_name, isCurrent: true });
            }
            for (const teacher of edit.teachers) {
              if (teacher.teacher_id !== subject.teacher_id && teachesSubject(teacher, subject.subject_name)) {
                candidates.push({ teacherId: teacher.teacher_id, teacherName: teacher.teacher_name, isCurrent: false });
              }
            }

            return (
              <optgroup key={subject.subject_id} label={subject.subject_name}>
                {candidates.map((candidate) => {
                  const value = choiceValue(subject.subject_id, candidate.teacherId);
                  // Busy in another section at this time (unless it's already this period's choice)
                  let busySection: string | null = null;
                  if (value !== currentValue) {
                    busySection = edit.busyIn(day, period, candidate.teacherId);
                  }
                  let label = `${subject.subject_name} - ${candidate.teacherName}`;
                  if (busySection) {
                    label = label + ` (busy in ${busySection})`;
                  } else if (!candidate.isCurrent && subject.teacher_id !== null) {
                    label = label + ' (becomes this class\'s teacher)';
                  }
                  return (
                    <option key={value} value={value} disabled={busySection !== null}>{label}</option>
                  );
                })}
                {subject.teacher_id === null && (
                  <option value={choiceValue(subject.subject_id, null)}>{subject.subject_name} (no teacher yet)</option>
                )}
              </optgroup>
            );
          })}
        </select>
        {slot && (
          <div className="text-[11px] text-gray-600 px-1 truncate">{slot.teacher_name || 'No teacher yet'}</div>
        )}
      </div>
    );
  };

  const renderViewCell = (day: number, period: number) => {
    const slot = findSlot(day, period);
    if (!slot) {
      return <div className="text-center text-gray-300 text-xs py-2">-</div>;
    }
    let secondLine = slot.teacher_name || 'No teacher yet';
    if (showSection) {
      secondLine = slot.section_name;
    }
    return (
      <div className={`rounded-lg border px-2 py-1 ${subjectColour(slot.subject_id)}`}>
        <div className="text-xs font-semibold text-gray-900 truncate">{slot.subject_name}</div>
        <div className="text-[11px] text-gray-600 truncate">{secondLine}</div>
      </div>
    );
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="sticky left-0 bg-white z-10 border border-gray-200 px-2 py-2 text-left text-xs text-gray-500">Day</th>
            {timetable.periods.map((period, index) => (
              <th key={index} className={`border border-gray-200 px-2 py-2 text-center ${period.is_break ? 'bg-gray-100 w-12' : 'min-w-[8.5rem]'}`}>
                <div className="text-xs font-semibold text-gray-700">{period.is_break ? period.name : `Period ${period.number}`}</div>
                <div className="text-[11px] font-normal text-gray-500">{period.start_time}-{period.end_time}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {timetable.days.map((day) => (
            <tr key={day.day}>
              <td className="sticky left-0 bg-white z-10 border border-gray-200 px-2 py-2 font-semibold text-gray-800">{day.name}</td>
              {timetable.periods.map((period, index) => {
                if (period.is_break || period.number === null) {
                  return <td key={index} className="border border-gray-200 bg-gray-100"></td>;
                }
                return (
                  <td key={index} className="border border-gray-200 p-1 align-top">
                    {edit ? renderEditCell(day.day, period.number) : renderViewCell(day.day, period.number)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
