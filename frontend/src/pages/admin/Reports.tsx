import React, { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { BarChart3, Download, Printer } from 'lucide-react';
import {
  getSchoolClasses, getExamTerms, getSectionAttendanceSummary, getSectionResults,
  getOversightDashboard, getTeachersOverview, downloadReport,
} from '../../services/api';
import type {
  SchoolClassSummary, ExamTerm, StudentMonthSummary, SectionResultSheet, ClassCoverage,
  TeacherOverview, LowAttendanceStudent,
} from '../../types';
import { ResultSheet } from '../../components/ResultSheet';
import { showError } from '../../utils/errorHandler';
import { todayText } from '../../utils/date';

type ReportName = 'attendance' | 'results' | 'syllabus' | 'teachers' | 'low-attendance';

const REPORTS: { name: ReportName; title: string; about: string }[] = [
  { name: 'attendance', title: 'Attendance', about: 'One section, one month: each student\'s days present, absent, late and on leave.' },
  { name: 'results', title: 'Exam Results', about: 'One section\'s result sheet for an exam term.' },
  { name: 'syllabus', title: 'Syllabus Coverage', about: 'How much of each subject every section has covered.' },
  { name: 'teachers', title: 'Teacher Activity', about: 'What each teacher did in the last 7 days.' },
  { name: 'low-attendance', title: 'Low Attendance', about: 'Students who are often absent this session.' },
];

// Reports for the admin. Each one can be downloaded as an Excel file, or viewed
// on the page and printed (the browser's Print window can also save it as a PDF).
const AdminReports: React.FC = () => {
  const [report, setReport] = useState<ReportName>('attendance');
  const [classes, setClasses] = useState<SchoolClassSummary[]>([]);
  const [terms, setTerms] = useState<ExamTerm[]>([]);
  const [loading, setLoading] = useState(true);

  // Options
  const [classId, setClassId] = useState('');
  const [sectionId, setSectionId] = useState('');
  const [month, setMonth] = useState(todayText().slice(0, 7));
  const [termId, setTermId] = useState('');

  // The report shown below (only the one for the chosen report is filled). It loads by itself
  // when the page opens and whenever the report or its options change.
  const [viewing, setViewing] = useState<ReportName | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportProblem, setReportProblem] = useState('');
  // Counts the loads, so an older, slower answer can't replace a newer one
  const loadNumber = useRef(0);
  const [viewHeading, setViewHeading] = useState('');
  const [attendanceRows, setAttendanceRows] = useState<StudentMonthSummary[]>([]);
  const [resultSheet, setResultSheet] = useState<SectionResultSheet | null>(null);
  const [coverage, setCoverage] = useState<ClassCoverage[]>([]);
  const [teachers, setTeachers] = useState<TeacherOverview[]>([]);
  const [lowAttendance, setLowAttendance] = useState<LowAttendanceStudent[]>([]);
  const [lowAttendancePercent, setLowAttendancePercent] = useState(75);

  useEffect(() => {
    const fetchLists = async () => {
      try {
        const classData = await getSchoolClasses();
        setClasses(Array.isArray(classData) ? classData : []);
        const termData = await getExamTerms();
        const termList: ExamTerm[] = Array.isArray(termData) ? termData : [];
        setTerms(termList);
        if (termList.length > 0) {
          setTermId(String(termList[0].id));
        }
        // Start with the first class that has sections, and its first section
        const classList: SchoolClassSummary[] = Array.isArray(classData) ? classData : [];
        for (const schoolClass of classList) {
          if (schoolClass.sections.length > 0) {
            setClassId(String(schoolClass.id));
            setSectionId(String(schoolClass.sections[0].id));
            break;
          }
        }
      } catch (error: any) {
        showError(error, 'Failed to load classes and exam terms');
      } finally {
        setLoading(false);
      }
    };
    fetchLists();
  }, []);

  // Show the chosen report as soon as the page is ready, and again whenever an option changes
  useEffect(() => {
    if (loading) return;
    showReport();
  }, [loading, report, sectionId, month, termId]);

  const chooseReport = (name: ReportName) => {
    setReport(name);
  };

  // A new class starts with its first section chosen
  const changeClass = (value: string) => {
    setClassId(value);
    let firstSection = '';
    for (const schoolClass of classes) {
      if (String(schoolClass.id) === value && schoolClass.sections.length > 0) {
        firstSection = String(schoolClass.sections[0].id);
      }
    }
    setSectionId(firstSection);
  };

  // The sections of the chosen class
  let sectionOptions: { id: number; full_name: string }[] = [];
  for (const schoolClass of classes) {
    if (String(schoolClass.id) === classId) {
      sectionOptions = schoolClass.sections;
    }
  }

  const findTermName = (): string => {
    for (const term of terms) {
      if (String(term.id) === termId) {
        return `${term.name} (${term.session_name})`;
      }
    }
    return '';
  };

  // An error message when the chosen report is missing an option, otherwise ''
  const missingOption = (): string => {
    if (report === 'attendance') {
      if (!sectionId) return 'Choose a class and section';
      if (!month) return 'Choose a month';
    }
    if (report === 'results') {
      if (!termId) return 'Choose an exam term';
      if (!sectionId) return 'Choose a class and section';
    }
    return '';
  };

  const handleDownload = async () => {
    const problem = missingOption();
    if (problem) {
      toast.error(problem);
      return;
    }
    try {
      if (report === 'attendance') {
        await downloadReport('attendance', { section_id: Number(sectionId), month: month });
      } else if (report === 'results') {
        await downloadReport('results', { term_id: Number(termId), section_id: Number(sectionId) });
      } else {
        await downloadReport(report);
      }
    } catch (error: any) {
      showError(error, 'Failed to download the report');
    }
  };

  const showReport = async () => {
    loadNumber.current = loadNumber.current + 1;
    const thisLoad = loadNumber.current;

    const problem = missingOption();
    if (problem) {
      setReportProblem(problem);
      setViewing(null);
      return;
    }
    setReportProblem('');
    setReportLoading(true);
    try {
      if (report === 'attendance') {
        const data = await getSectionAttendanceSummary(Number(sectionId), month);
        setAttendanceRows(Array.isArray(data.students) ? data.students : []);
        setViewHeading(`Attendance · ${data.section_name} · ${data.month}`);
      }
      if (report === 'results') {
        const data = await getSectionResults(Number(termId), Number(sectionId));
        setResultSheet(data);
        setViewHeading(`Exam Results · ${data.section_name} · ${findTermName()}`);
      }
      if (report === 'syllabus') {
        const data = await getOversightDashboard();
        setCoverage(Array.isArray(data.syllabus_coverage) ? data.syllabus_coverage : []);
        setViewHeading('Syllabus Coverage · whole school');
      }
      if (report === 'teachers') {
        const data = await getTeachersOverview();
        setTeachers(Array.isArray(data.teachers) ? data.teachers : []);
        setViewHeading(`Teacher Activity · ${data.week_start} to ${data.today}`);
      }
      if (report === 'low-attendance') {
        const data = await getOversightDashboard();
        setLowAttendance(Array.isArray(data.low_attendance) ? data.low_attendance : []);
        setLowAttendancePercent(data.low_attendance_percent);
        setViewHeading(`Low Attendance · below ${data.low_attendance_percent}% this session`);
      }
      // Only the newest load is shown
      if (thisLoad === loadNumber.current) {
        setViewing(report);
      }
    } catch (error: any) {
      showError(error, 'Failed to load the report');
    } finally {
      if (thisLoad === loadNumber.current) {
        setReportLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="no-print">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2"><BarChart3 size={28} className="text-primary-600" /> Reports</h1>
        <p className="text-gray-600 mt-2">Each report shows below as soon as you choose it. Download it as an Excel file, or print it (Print can also save it as a PDF).</p>
      </div>

      {/* Report picker */}
      <div className="no-print grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {REPORTS.map((item) => (
          <button
            key={item.name}
            onClick={() => chooseReport(item.name)}
            className={`text-left p-4 rounded-xl border-2 transition-all ${report === item.name ? 'border-primary-600 bg-primary-50' : 'border-gray-200 bg-white hover:border-gray-300'}`}
          >
            <div className="font-semibold text-gray-900">{item.title}</div>
            <div className="text-xs text-gray-500 mt-1">{item.about}</div>
          </button>
        ))}
      </div>

      {/* Options and buttons */}
      <div className="no-print card space-y-4">
        {(report === 'attendance' || report === 'results') && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {report === 'results' && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Exam term</label>
                <select value={termId} onChange={(e) => setTermId(e.target.value)} className="input">
                  <option value="">Choose a term</option>
                  {terms.map((term) => (
                    <option key={term.id} value={term.id}>{term.name} ({term.session_name})</option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm text-gray-600 mb-1">Class</label>
              <select value={classId} onChange={(e) => changeClass(e.target.value)} className="input">
                <option value="">Choose a class</option>
                {classes.map((schoolClass) => (
                  <option key={schoolClass.id} value={schoolClass.id}>{schoolClass.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Section</label>
              <select value={sectionId} onChange={(e) => setSectionId(e.target.value)} className="input" disabled={classId === ''}>
                <option value="">Choose a section</option>
                {sectionOptions.map((section) => (
                  <option key={section.id} value={section.id}>{section.full_name}</option>
                ))}
              </select>
            </div>
            {report === 'attendance' && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Month</label>
                <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} className="input" />
              </div>
            )}
          </div>
        )}
        {report !== 'attendance' && report !== 'results' && (
          <p className="text-sm text-gray-500">This report covers the whole school. No options needed.</p>
        )}
        <div className="flex flex-wrap gap-2">
          <button onClick={handleDownload} className="btn btn-primary flex items-center gap-2"><Download size={16} /> Download Excel</button>
          {viewing === report && (
            <button onClick={() => window.print()} className="btn btn-secondary flex items-center gap-2"><Printer size={16} /> Print / Save as PDF</button>
          )}
        </div>
      </div>

      {/* What's missing before the report can be shown, or that it's loading */}
      {reportProblem !== '' && (
        <div className="no-print card text-sm text-gray-600">{reportProblem} to see this report.</div>
      )}
      {reportProblem === '' && reportLoading && viewing !== report && (
        <div className="no-print card text-sm text-gray-400">Loading the report...</div>
      )}

      {/* The printable view */}
      {viewing === report && (
        <div className="print-area card space-y-4">
          <div className="border-b border-gray-200 pb-3">
            <h2 className="text-xl font-bold text-gray-900">{viewHeading}</h2>
            <p className="text-sm text-gray-500">Printed on {todayText()}</p>
          </div>

          {viewing === 'attendance' && (
            attendanceRows.length === 0 ? (
              <p className="text-sm text-gray-500">No students in this section.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Roll</th>
                      <th>Name</th>
                      <th>Present</th>
                      <th>Absent</th>
                      <th>Late</th>
                      <th>Leave</th>
                      <th>Attendance %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceRows.map((student) => (
                      <tr key={student.student_id}>
                        <td>{student.roll_number || '-'}</td>
                        <td>{student.name}</td>
                        <td>{student.present}</td>
                        <td>{student.absent}</td>
                        <td>{student.late}</td>
                        <td>{student.leave}</td>
                        <td className={student.percentage !== null && student.percentage < 75 ? 'text-red-600 font-semibold' : ''}>
                          {student.percentage !== null ? `${student.percentage}%` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}

          {viewing === 'results' && resultSheet && (
            <ResultSheet sheet={resultSheet} />
          )}

          {viewing === 'syllabus' && (
            coverage.length === 0 ? (
              <p className="text-sm text-gray-500">No class has sections and subjects with chapters yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Section</th>
                      <th>Subject</th>
                      <th>Teacher</th>
                      <th>Chapters done</th>
                      <th>Covered</th>
                    </tr>
                  </thead>
                  <tbody>
                    {coverage.map((schoolClass) => (
                      schoolClass.sections.map((section) => (
                        section.subjects.map((subject) => (
                          <tr key={`${section.section_id}-${subject.subject_name}`}>
                            <td>{section.section_name}</td>
                            <td>{subject.subject_name}</td>
                            <td>{subject.teacher_name || '-'}</td>
                            <td>{subject.chapters_done} / {subject.chapter_count}</td>
                            <td>{subject.percentage}%</td>
                          </tr>
                        ))
                      ))
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}

          {viewing === 'teachers' && (
            teachers.length === 0 ? (
              <p className="text-sm text-gray-500">No teachers yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Teacher</th>
                      <th>Last login</th>
                      <th>Attendance days</th>
                      <th>Diary</th>
                      <th>Assignments</th>
                      <th>Class tests</th>
                      <th>Syllabus updates</th>
                      <th>Papers pending</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teachers.map((teacher) => (
                      <tr key={teacher.id}>
                        <td className="font-medium">{teacher.name}</td>
                        <td>{teacher.last_login || 'Never'}</td>
                        <td>{teacher.this_week.attendance_days_marked}</td>
                        <td>{teacher.this_week.diary_entries}</td>
                        <td>{teacher.this_week.assignments}</td>
                        <td>{teacher.this_week.class_tests}</td>
                        <td>{teacher.this_week.progress_updates}</td>
                        <td className={teacher.papers_pending > 0 ? 'text-red-600 font-semibold' : ''}>{teacher.papers_pending}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}

          {viewing === 'low-attendance' && (
            lowAttendance.length === 0 ? (
              <p className="text-sm text-gray-500">No student is below {lowAttendancePercent}%.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="table text-sm">
                  <thead>
                    <tr>
                      <th>Section</th>
                      <th>Roll</th>
                      <th>Name</th>
                      <th>Attendance %</th>
                      <th>Days absent</th>
                      <th>Days counted</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lowAttendance.map((student) => (
                      <tr key={student.student_id}>
                        <td>{student.section_name || '-'}</td>
                        <td>{student.roll_number || '-'}</td>
                        <td>{student.name}</td>
                        <td className="text-red-600 font-semibold">{student.percentage}%</td>
                        <td>{student.absent}</td>
                        <td>{student.days_counted}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};

export default AdminReports;
