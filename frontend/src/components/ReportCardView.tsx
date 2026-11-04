import React from 'react';
import type { ReportCard } from '../types';

interface ReportCardViewProps {
  card: ReportCard;
}

const RESULT_COLOURS: Record<string, string> = {
  Pass: 'text-green-700',
  Fail: 'text-red-700',
  Incomplete: 'text-gray-600',
};

// One student's report card for a term: every subject's marks and grade, the totals,
// position in the section, attendance during the term, and the class incharge's remarks.
// Wrapped in "print-area" so the Print button prints only the card.
export const ReportCardView: React.FC<ReportCardViewProps> = ({ card }) => {
  let attendanceText = '-';
  if (card.attendance.percentage !== null) {
    attendanceText = `${card.attendance.percentage}% (present ${card.attendance.present + card.attendance.late} of ${card.attendance.present + card.attendance.late + card.attendance.absent} days)`;
  }

  return (
    <div className="print-area card space-y-6">
      <div className="text-center border-b border-gray-200 pb-4">
        <h2 className="text-2xl font-bold text-gray-900">Report Card</h2>
        <p className="text-gray-600">{card.term.name} · Session {card.term.session_name}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
        <div><span className="text-gray-500">Name: </span><span className="font-semibold">{card.name}</span></div>
        <div><span className="text-gray-500">Class: </span><span className="font-semibold">{card.section_name}</span></div>
        <div><span className="text-gray-500">Roll No.: </span><span className="font-semibold">{card.roll_number || '-'}</span></div>
        <div><span className="text-gray-500">Admission No.: </span><span className="font-semibold">{card.admission_number || '-'}</span></div>
        <div><span className="text-gray-500">Guardian: </span><span className="font-semibold">{card.guardian_name || '-'}</span></div>
        <div><span className="text-gray-500">Class Incharge: </span><span className="font-semibold">{card.incharge_name || '-'}</span></div>
      </div>

      <div className="overflow-x-auto">
        <table className="table text-sm">
          <thead>
            <tr>
              <th>Subject</th>
              <th>Total</th>
              <th>Passing</th>
              <th>Obtained</th>
              <th>%</th>
              <th>Grade</th>
              <th>Remarks</th>
            </tr>
          </thead>
          <tbody>
            {card.subjects.map((subject) => {
              let obtainedText = '-';
              if (subject.is_absent) {
                obtainedText = 'Absent';
              } else if (subject.obtained_marks !== null) {
                obtainedText = subject.obtained_marks;
              }

              let passText = 'Not marked yet';
              if (subject.passed === true) {
                passText = 'Pass';
              }
              if (subject.passed === false) {
                passText = 'Fail';
              }

              return (
                <tr key={subject.paper_id}>
                  <td className="font-semibold">{subject.subject_name}</td>
                  <td>{subject.total_marks}</td>
                  <td>{subject.passing_marks}</td>
                  <td className={subject.passed === false ? 'text-red-600 font-semibold' : ''}>{obtainedText}</td>
                  <td>{subject.percentage !== null ? subject.percentage : '-'}</td>
                  <td>{subject.grade || '-'}</td>
                  <td className={subject.passed === false ? 'text-red-600' : 'text-gray-600'}>{passText}</td>
                </tr>
              );
            })}
            <tr className="font-semibold bg-gray-50">
              <td>Total</td>
              <td>{card.total_marks}</td>
              <td></td>
              <td>{card.total_obtained}</td>
              <td>{card.percentage !== null ? card.percentage : '-'}</td>
              <td>{card.grade || '-'}</td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
        <div className="border border-gray-200 rounded-xl p-3">
          <div className="text-xs text-gray-500">Result</div>
          <div className={`text-xl font-bold ${RESULT_COLOURS[card.result]}`}>{card.result}</div>
        </div>
        <div className="border border-gray-200 rounded-xl p-3">
          <div className="text-xs text-gray-500">Position</div>
          <div className="text-xl font-bold text-gray-900">{card.position ? `${card.position} of ${card.class_strength}` : '-'}</div>
        </div>
        <div className="border border-gray-200 rounded-xl p-3">
          <div className="text-xs text-gray-500">Percentage</div>
          <div className="text-xl font-bold text-gray-900">{card.percentage !== null ? `${card.percentage}%` : '-'}</div>
        </div>
        <div className="border border-gray-200 rounded-xl p-3">
          <div className="text-xs text-gray-500">Grade</div>
          <div className="text-xl font-bold text-gray-900">{card.grade || '-'}</div>
        </div>
      </div>

      <div className="text-sm space-y-2">
        <div><span className="text-gray-500">Attendance during the term: </span><span className="font-semibold">{attendanceText}</span></div>
        <div>
          <div className="text-gray-500">Class incharge's remarks:</div>
          <div className="mt-1 p-3 bg-gray-50 rounded-lg min-h-[3rem]">{card.remarks || <span className="text-gray-400">No remarks</span>}</div>
        </div>
      </div>

      <p className="text-xs text-gray-400">Grades: A+ 80% and above, A 70%, B 60%, C 50%, D 40%, E 33%, F below 33%.</p>
    </div>
  );
};
