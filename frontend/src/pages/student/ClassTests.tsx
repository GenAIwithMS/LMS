import React, { useState, useEffect } from 'react';
import { ClipboardCheck } from 'lucide-react';
import { getClassTests } from '../../services/api';
import type { ClassTest } from '../../types';
import { showError } from '../../utils/errorHandler';

// A student's class tests: every test taken in their section, with their own marks.
const StudentClassTests: React.FC = () => {
  const [tests, setTests] = useState<ClassTest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const data = await getClassTests();
        setTests(Array.isArray(data) ? data : []);
      } catch (error: any) {
        showError(error, 'Failed to load your class tests');
      } finally {
        setLoading(false);
      }
    };
    fetchTests();
  }, []);

  // "8.5 / 10", "Absent" or "Not marked yet"
  const myMarksText = (test: ClassTest) => {
    if (test.was_absent) {
      return 'Absent';
    }
    if (test.my_marks === null || test.my_marks === undefined) {
      return 'Not marked yet';
    }
    return `${test.my_marks} / ${test.total_marks}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Class Tests</h1>
        <p className="text-gray-600 mt-2">Your marks in the tests taken in your class</p>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <ClipboardCheck size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Tests ({tests.length})</h2>
        </div>
        {tests.length === 0 ? (
          <p className="text-sm text-gray-500">No class tests yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Subject</th>
                  <th>Title</th>
                  <th>Chapter</th>
                  <th>My Marks</th>
                  <th>Class Average</th>
                </tr>
              </thead>
              <tbody>
                {tests.map((test) => (
                  <tr key={test.id}>
                    <td>{test.date}</td>
                    <td>{test.subject_name}</td>
                    <td className="font-semibold">{test.title}</td>
                    <td>{test.chapter_title || '-'}</td>
                    <td>
                      {test.was_absent ? (
                        <span className="text-red-600">{myMarksText(test)}</span>
                      ) : test.my_marks === null || test.my_marks === undefined ? (
                        <span className="text-gray-400">{myMarksText(test)}</span>
                      ) : (
                        <span className="font-semibold">{myMarksText(test)}</span>
                      )}
                    </td>
                    <td>{test.average !== null ? test.average : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentClassTests;
