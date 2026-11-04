import React from 'react';
import type { BellPeriod, TimetableSlot } from '../types';

interface TimetableGridProps {
  timetable: {
    days: { day: number; name: string }[];
    periods: BellPeriod[];
    slots: TimetableSlot[];
  };
  // A teacher's own week shows the section of each period instead of the teacher
  showSection?: boolean;
  // Give this to let the admin click a period to change it (the choosing happens in a panel next to the grid)
  edit?: {
    selected: { day: number; period: number } | null;
    onSelect: (day: number, period: number) => void;
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

export const subjectColour = (subjectId: number | null): string => {
  if (subjectId === null) {
    return 'bg-gray-50 border-gray-200';
  }
  return SUBJECT_COLOURS[subjectId % SUBJECT_COLOURS.length];
};

// The weekly timetable like a college timetable: days down the side, the periods
// (with their times) across the top, and breaks as a shaded column.
export const TimetableGrid: React.FC<TimetableGridProps> = ({ timetable, showSection, edit }) => {
  const findSlot = (day: number, period: number): TimetableSlot | undefined => {
    return timetable.slots.find((slot) => slot.day === day && slot.period === period);
  };

  // What a filled period shows: the subject, then the teacher (or the section for a teacher's own week)
  const renderSlotText = (slot: TimetableSlot) => {
    let secondLine = slot.teacher_name || 'No teacher yet';
    if (showSection) {
      secondLine = slot.section_name;
    }
    return (
      <>
        <div className="text-xs font-semibold text-gray-900 leading-tight break-words">{slot.subject_name}</div>
        <div className="text-[11px] text-gray-600 leading-tight break-words">{secondLine}</div>
      </>
    );
  };

  const renderEditCell = (day: number, period: number) => {
    if (!edit) return null;
    const slot = findSlot(day, period);
    const isSelected = edit.selected !== null && edit.selected.day === day && edit.selected.period === period;

    let look = 'border-dashed border-gray-300 bg-white hover:border-primary-400';
    if (slot) {
      look = subjectColour(slot.subject_id) + ' hover:shadow';
    }
    if (isSelected) {
      look = look + ' ring-2 ring-primary-500';
    }

    return (
      <button
        type="button"
        onClick={() => edit.onSelect(day, period)}
        className={`w-full min-h-[3rem] rounded-lg border px-2 py-1 text-left ${look}`}
        title="Click to choose the subject and teacher"
      >
        {slot ? renderSlotText(slot) : <div className="text-xs text-gray-400">Free</div>}
      </button>
    );
  };

  const renderViewCell = (day: number, period: number) => {
    const slot = findSlot(day, period);
    if (!slot) {
      return <div className="text-center text-gray-300 text-xs py-2">-</div>;
    }
    return (
      <div className={`rounded-lg border px-2 py-1 ${subjectColour(slot.subject_id)}`}>
        {renderSlotText(slot)}
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
              <th key={index} className={`border border-gray-200 px-2 py-2 text-center ${period.is_break ? 'bg-gray-100 w-12' : 'min-w-[7.5rem]'}`}>
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
