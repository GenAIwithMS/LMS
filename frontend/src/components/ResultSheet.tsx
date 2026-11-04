import React from 'react';
import type { SectionResultSheet } from '../types';

interface ResultSheetProps {
  sheet: SectionResultSheet;
  // Give this to make each student's name open their report card
  onOpenStudent?: (studentId: number) => void;
}

const RESULT_COLOURS: Record<string, string> = {
  Pass: 'bg-green-100 text-green-800',
  Fail: 'bg-red-100 text-red-800',
  Incomplete: 'bg-gray-100 text-gray-600',
};

// A section's result sheet for a term: every student's marks in each subject,
// the total, percentage, grade, position in the section and the result.
export const ResultSheet: React.FC<ResultSheetProps> = ({ sheet, onOpenStudent }) => {
  if (sheet.students.length === 0) {
    return <p className="text-sm text-gray-500">No students in this section for this term.</p>;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-600">
        {sheet.passed_count} of {sheet.students.length} students passed
        {sheet.incharge_name ? ` · Class incharge: ${sheet.incharge_name}` : ''}
      </p>
      <div className="overflow-x-auto">
        <table className="table text-sm">
          <thead>
            <tr>
              <th>Roll</th>
              <th>Name</th>
              {sheet.subjects.map((subject) => (
                <th key={subject.paper_id}>{subject.subject_name} <span className="font-normal text-gray-400">/{subject.total_marks}</span></th>
              ))}
              <th>Total</th>
              <th>%</th>
              <th>Grade</th>
              <th>Position</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {sheet.students.map((student) => (
              <tr key={student.student_id}>
                <td>{student.roll_number || '-'}</td>
                <td>
                  {onOpenStudent ? (
                    <button onClick={() => onOpenStudent(student.student_id)} className="text-primary-600 hover:underline font-medium">{student.name}</button>
                  ) : (
                    student.name
                  )}
                </td>
                {student.subjects.map((subject) => {
                  let text = '-';
                  if (subject.is_absent) {
                    text = 'Abs';
                  } else if (subject.obtained_marks !== null) {
                    text = subject.obtained_marks;
                  }
                  return (
                    <td key={subject.paper_id} className={subject.passed === false ? 'text-red-600 font-semibold' : ''}>{text}</td>
                  );
                })}
                <td className="font-semibold">{student.total_obtained}/{student.total_marks}</td>
                <td>{student.percentage !== null ? student.percentage : '-'}</td>
                <td>{student.grade || '-'}</td>
                <td>{student.position || '-'}</td>
                <td>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${RESULT_COLOURS[student.result]}`}>{student.result}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500">Red marks are below the passing marks. "Abs" means absent.</p>
    </div>
  );
};
