import React from 'react';
import type { Timetable, TimetableSlot } from '../types';

interface TimetableGridProps {
  timetable: Timetable;
  // Give these two to let the admin choose the subject of each period
  subjects?: { subject_id: number; subject_name: string }[];
  onChange?: (day: number, period: number, subjectId: number | null) => void;
  // A teacher's own week shows the section of each period instead of the teacher
  showSection?: boolean;
}

// The weekly timetable: periods down the side, Monday to Saturday across the top.
export const TimetableGrid: React.FC<TimetableGridProps> = ({ timetable, subjects, onChange, showSection }) => {
  const canEdit = subjects !== undefined && onChange !== undefined;

  const findSlot = (day: number, period: number): TimetableSlot | undefined => {
    return timetable.slots.find((slot) => slot.day === day && slot.period === period);
  };

  const periodNumbers: number[] = [];
  for (let period = 1; period <= timetable.periods_per_day; period++) {
    periodNumbers.push(period);
  }

  return (
    <div className="overflow-x-auto">
      <table className="table text-sm">
        <thead>
          <tr>
            <th>Period</th>
            {timetable.days.map((day) => (
              <th key={day.day}>{day.name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {periodNumbers.map((period) => (
            <tr key={period}>
              <td className="font-semibold">{period}</td>
              {timetable.days.map((day) => {
                const slot = findSlot(day.day, period);

                if (canEdit) {
                  return (
                    <td key={day.day} className="min-w-[8rem]">
                      <select
                        value={slot ? String(slot.subject_id) : ''}
                        onChange={(e) => onChange(day.day, period, e.target.value ? Number(e.target.value) : null)}
                        className="input py-1 text-sm"
                      >
                        <option value="">Free</option>
                        {subjects.map((subject) => (
                          <option key={subject.subject_id} value={subject.subject_id}>{subject.subject_name}</option>
                        ))}
                      </select>
                      {slot && (
                        <div className="text-xs text-gray-500 mt-1">{slot.teacher_name || 'No teacher yet'}</div>
                      )}
                    </td>
                  );
                }

                if (!slot) {
                  return <td key={day.day} className="text-gray-300 min-w-[7rem]">-</td>;
                }
                return (
                  <td key={day.day} className="min-w-[7rem]">
                    <div className="font-semibold text-gray-900">{slot.subject_name}</div>
                    <div className="text-xs text-gray-500">
                      {showSection ? slot.section_name : (slot.teacher_name || 'No teacher yet')}
                    </div>
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
