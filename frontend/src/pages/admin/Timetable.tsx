import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { CalendarDays, Send, Settings, Printer, Plus, Trash2, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { getTimetableDraft, setTimetableSlot, clearSectionTimetable, getPublishCheck, publishTimetable, saveTimetableSettings } from '../../services/api';
import type { SchoolTimetableDraft, DraftSection } from '../../types';
import { TimetableGrid } from '../../components/TimetableGrid';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

type Tab = 'class' | 'school' | 'load';

// One row of the bell schedule while editing it
interface BellRow {
  name: string;
  start_time: string;
  end_time: string;
  is_break: boolean;
}

const ALL_DAYS = [
  { day: 1, name: 'Monday' },
  { day: 2, name: 'Tuesday' },
  { day: 3, name: 'Wednesday' },
  { day: 4, name: 'Thursday' },
  { day: 5, name: 'Friday' },
  { day: 6, name: 'Saturday' },
  { day: 7, name: 'Sunday' },
];

// The school timetable. The admin makes each section's week here (a draft), then
// presses Publish: from then on every teacher sees their own periods and every
// student sees their section's timetable. Changes stay in the draft until published again.
const AdminTimetable: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [draft, setDraft] = useState<SchoolTimetableDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('class');
  const [selectedSectionId, setSelectedSectionId] = useState<number | null>(null);
  const [schoolDay, setSchoolDay] = useState<number>(1);

  // Publishing
  const [isPublishOpen, setIsPublishOpen] = useState(false);
  const [publishErrors, setPublishErrors] = useState<string[]>([]);
  const [publishWarnings, setPublishWarnings] = useState<string[]>([]);

  // Emptying a section's timetable
  const [isClearOpen, setIsClearOpen] = useState(false);

  // Bell schedule and school days
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [bellRows, setBellRows] = useState<BellRow[]>([]);
  const [schoolDays, setSchoolDays] = useState<number[]>([]);

  useEffect(() => {
    fetchDraft();
  }, []);

  // The spinner shows only on the first load, so the page doesn't blank out after each change
  const fetchDraft = async () => {
    try {
      const data: SchoolTimetableDraft = await getTimetableDraft();
      setDraft(data);

      // Choose a section: the one in the address bar, or the first one
      if (selectedSectionId === null && data.sections.length > 0) {
        const fromAddress = Number(searchParams.get('section'));
        const found = data.sections.find((section) => section.section_id === fromAddress);
        if (found) {
          setSelectedSectionId(found.section_id);
        } else {
          setSelectedSectionId(data.sections[0].section_id);
        }
      }
      if (data.days.length > 0 && !data.days.some((day) => day.day === schoolDay)) {
        setSchoolDay(data.days[0].day);
      }
    } catch (error: any) {
      showError(error, 'Failed to load the timetable');
    } finally {
      setLoading(false);
    }
  };

  // ---------------- Editing a section's week

  const selectedSection: DraftSection | undefined = draft?.sections.find((section) => section.section_id === selectedSectionId);

  // Where a teacher already is on this day and period (another section), or null
  const busyIn = (day: number, period: number, teacherId: number): string | null => {
    if (!draft) return null;
    for (const section of draft.sections) {
      if (section.section_id === selectedSectionId) continue;
      for (const slot of section.slots) {
        if (slot.day === day && slot.period === period && slot.teacher_id === teacherId) {
          return section.section_name;
        }
      }
    }
    return null;
  };

  const handleSlotChange = async (day: number, period: number, subjectId: number | null, teacherId: number | null) => {
    if (selectedSectionId === null) return;
    try {
      const data = await setTimetableSlot(selectedSectionId, { day, period, subject_id: subjectId, teacher_id: teacherId });
      // Say so when a different teacher took over the subject in this section
      if (data.message && data.message.includes('now teaches')) {
        showSuccess(data.message);
      }
      fetchDraft();
    } catch (error: any) {
      // For example: the teacher is already in another section at this time
      showError(error, 'Failed to change the period');
    }
  };

  const handleClear = async () => {
    if (selectedSectionId === null) return;
    try {
      const data = await clearSectionTimetable(selectedSectionId);
      showSuccess(data.message || 'Timetable emptied');
      setIsClearOpen(false);
      fetchDraft();
    } catch (error: any) {
      showError(error, 'Failed to empty the timetable');
    }
  };

  // ---------------- Publishing

  const openPublish = async () => {
    try {
      const data = await getPublishCheck();
      setPublishErrors(Array.isArray(data.errors) ? data.errors : []);
      setPublishWarnings(Array.isArray(data.warnings) ? data.warnings : []);
      setIsPublishOpen(true);
    } catch (error: any) {
      showError(error, 'Failed to check the timetable');
    }
  };

  const handlePublish = async () => {
    try {
      const data = await publishTimetable();
      showSuccess(data.message || 'Timetable published');
      setIsPublishOpen(false);
      fetchDraft();
    } catch (error: any) {
      showError(error, 'Failed to publish the timetable');
    }
  };

  // ---------------- Bell schedule and school days

  const openSettings = () => {
    if (!draft) return;
    const rows: BellRow[] = [];
    for (const period of draft.periods) {
      rows.push({ name: period.name, start_time: period.start_time, end_time: period.end_time, is_break: period.is_break });
    }
    setBellRows(rows);
    const days: number[] = [];
    for (const day of draft.days) {
      days.push(day.day);
    }
    setSchoolDays(days);
    setIsSettingsOpen(true);
  };

  const changeBellRow = (index: number, field: keyof BellRow, value: string | boolean) => {
    const rows: BellRow[] = [];
    for (let i = 0; i < bellRows.length; i++) {
      if (i === index) {
        rows.push({ ...bellRows[i], [field]: value });
      } else {
        rows.push(bellRows[i]);
      }
    }
    setBellRows(rows);
  };

  const addBellRow = (isBreak: boolean) => {
    // Start right after the last period
    let start = '08:00';
    if (bellRows.length > 0) {
      start = bellRows[bellRows.length - 1].end_time;
    }
    let name = 'Break';
    if (!isBreak) {
      let classCount = 0;
      for (const row of bellRows) {
        if (!row.is_break) classCount = classCount + 1;
      }
      name = `Period ${classCount + 1}`;
    }
    setBellRows([...bellRows, { name: name, start_time: start, end_time: start, is_break: isBreak }]);
  };

  const removeBellRow = (index: number) => {
    const rows: BellRow[] = [];
    for (let i = 0; i < bellRows.length; i++) {
      if (i !== index) rows.push(bellRows[i]);
    }
    setBellRows(rows);
  };

  const toggleDay = (day: number) => {
    if (schoolDays.includes(day)) {
      setSchoolDays(schoolDays.filter((one) => one !== day));
    } else {
      setSchoolDays([...schoolDays, day]);
    }
  };

  const handleSaveSettings = async () => {
    for (const row of bellRows) {
      if (row.name.trim() === '' || row.start_time === '' || row.end_time === '') {
        toast.error('Every row needs a name, a start time and an end time');
        return;
      }
    }
    try {
      const data = await saveTimetableSettings({ days: schoolDays, periods: bellRows });
      showSuccess(data.message || 'Timetable settings saved');
      setIsSettingsOpen(false);
      fetchDraft();
    } catch (error: any) {
      showError(error, 'Failed to save the timetable settings');
    }
  };

  if (loading || !draft) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Sections grouped by class, for the picker
  const classGroups: { className: string; sections: DraftSection[] }[] = [];
  for (const section of draft.sections) {
    let group = classGroups.find((one) => one.className === section.class_name);
    if (!group) {
      group = { className: section.class_name, sections: [] };
      classGroups.push(group);
    }
    group.sections.push(section);
  }

  const noTeacherSubjects: string[] = [];
  if (selectedSection) {
    for (const subject of selectedSection.subjects) {
      if (subject.teacher_id === null) noTeacherSubjects.push(subject.subject_name);
    }
  }

  const status = draft.status;

  return (
    <div className="space-y-6">
      {/* Title, status and the main buttons */}
      <div className="no-print flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Timetable</h1>
          <p className="text-gray-600 mt-2">Make every section's weekly timetable, then publish it to teachers and students.</p>
          <div className="mt-2 text-sm">
            {!status.is_published ? (
              <span className="px-2 py-1 rounded-full bg-orange-100 text-orange-800 font-medium">Not published yet: teachers and students can't see it</span>
            ) : status.has_unpublished_changes ? (
              <span className="px-2 py-1 rounded-full bg-yellow-100 text-yellow-800 font-medium">Changes not published yet (last published {status.published_at})</span>
            ) : (
              <span className="px-2 py-1 rounded-full bg-green-100 text-green-800 font-medium">Published {status.published_at}{status.published_by ? ` by ${status.published_by}` : ''}</span>
            )}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={openSettings} className="btn btn-secondary flex items-center gap-2"><Settings size={16} /> Bell Schedule & Days</button>
          <button onClick={() => window.print()} className="btn btn-secondary flex items-center gap-2"><Printer size={16} /> Print</button>
          <button onClick={openPublish} className="btn btn-primary flex items-center gap-2"><Send size={16} /> Publish</button>
        </div>
      </div>

      <div className="no-print flex flex-wrap gap-2 border-b border-gray-200">
        <button onClick={() => setTab('class')} className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${tab === 'class' ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}>By Class</button>
        <button onClick={() => setTab('school')} className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${tab === 'school' ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}>Whole School</button>
        <button onClick={() => setTab('load')} className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${tab === 'load' ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-800'}`}>Teachers' Load</button>
      </div>

      {draft.sections.length === 0 && (
        <div className="card text-gray-600">
          No sections yet. Add sections and subjects on the <button onClick={() => navigate('/admin/classes')} className="text-primary-600 hover:underline">Classes</button> page first.
        </div>
      )}

      {/* ---------------- One section at a time, editable */}
      {tab === 'class' && draft.sections.length > 0 && (
        <>
          <div className="no-print card space-y-3">
            {classGroups.map((group) => (
              <div key={group.className} className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-semibold text-gray-700 w-20">{group.className}</span>
                {group.sections.map((section) => (
                  <button
                    key={section.section_id}
                    onClick={() => setSelectedSectionId(section.section_id)}
                    className={`px-3 py-1 rounded-lg text-sm border ${section.section_id === selectedSectionId ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300 hover:border-primary-400'}`}
                  >
                    {section.section_name.replace(group.className + ' - ', 'Section ')}
                    <span className="ml-1 text-xs opacity-75">({section.slots.length})</span>
                  </button>
                ))}
              </div>
            ))}
          </div>

          {selectedSection && (
            <div className="print-area card space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2"><CalendarDays size={20} className="text-primary-600" /> {selectedSection.section_name}</h2>
                  <p className="text-sm text-gray-500">Class incharge: {selectedSection.incharge_name || 'not chosen yet'} · {selectedSection.student_count} students · {selectedSection.slots.length} periods a week</p>
                </div>
                <button onClick={() => setIsClearOpen(true)} className="no-print btn btn-secondary text-sm text-red-600 flex items-center gap-1"><Trash2 size={14} /> Empty this timetable</button>
              </div>

              {selectedSection.subjects.length === 0 ? (
                <div className="no-print p-3 rounded-lg bg-orange-50 text-orange-800 text-sm">
                  {selectedSection.class_name} has no subjects yet, so there is nothing to put in the periods.
                  Add its subjects and their teachers on the <button onClick={() => navigate(`/admin/classes/${selectedSection.class_id}`)} className="underline font-medium">{selectedSection.class_name} page</button>.
                </div>
              ) : (
                <>
                  {noTeacherSubjects.length > 0 && (
                    <div className="no-print p-3 rounded-lg bg-yellow-50 text-yellow-800 text-sm">
                      No teacher yet for: {noTeacherSubjects.join(', ')}. You can still put them in the timetable;
                      choose their teachers on the <button onClick={() => navigate(`/admin/classes/${selectedSection.class_id}`)} className="underline font-medium">{selectedSection.class_name} page</button>.
                    </div>
                  )}
                  <p className="no-print text-sm text-gray-500">
                    Choose the subject and teacher for each period. Every teacher who teaches the subject is offered;
                    one who is busy in another section at that time is greyed out. Choosing a different teacher makes them this class's teacher of that subject.
                  </p>
                  <TimetableGrid
                    timetable={{ days: draft.days, periods: draft.periods, slots: selectedSection.slots }}
                    edit={{ subjects: selectedSection.subjects, teachers: draft.teachers, busyIn: busyIn, onChange: handleSlotChange }}
                  />
                </>
              )}
            </div>
          )}
        </>
      )}

      {/* ---------------- The whole school on one day */}
      {tab === 'school' && draft.sections.length > 0 && (
        <div className="print-area card space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-xl font-bold text-gray-900">Whole School</h2>
            <div className="no-print flex flex-wrap gap-1">
              {draft.days.map((day) => (
                <button
                  key={day.day}
                  onClick={() => setSchoolDay(day.day)}
                  className={`px-3 py-1 rounded-lg text-sm border ${day.day === schoolDay ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'}`}
                >
                  {day.name}
                </button>
              ))}
            </div>
          </div>
          <p className="text-sm text-gray-500">{ALL_DAYS.find((day) => day.day === schoolDay)?.name}: every section's periods.</p>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr>
                  <th className="sticky left-0 bg-white z-10 border border-gray-200 px-2 py-2 text-left text-xs text-gray-500">Section</th>
                  {draft.periods.map((period, index) => (
                    <th key={index} className={`border border-gray-200 px-2 py-2 text-center ${period.is_break ? 'bg-gray-100 w-12' : 'min-w-[8rem]'}`}>
                      <div className="text-xs font-semibold text-gray-700">{period.is_break ? period.name : `Period ${period.number}`}</div>
                      <div className="text-[11px] font-normal text-gray-500">{period.start_time}-{period.end_time}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {draft.sections.map((section) => (
                  <tr key={section.section_id}>
                    <td className="sticky left-0 bg-white z-10 border border-gray-200 px-2 py-2 font-semibold text-gray-800 whitespace-nowrap">{section.section_name}</td>
                    {draft.periods.map((period, index) => {
                      if (period.is_break || period.number === null) {
                        return <td key={index} className="border border-gray-200 bg-gray-100"></td>;
                      }
                      const slot = section.slots.find((one) => one.day === schoolDay && one.period === period.number);
                      return (
                        <td key={index} className="border border-gray-200 px-2 py-1 align-top">
                          {slot ? (
                            <>
                              <div className="text-xs font-semibold text-gray-900">{slot.subject_name}</div>
                              <div className="text-[11px] text-gray-600">{slot.teacher_name || 'No teacher yet'}</div>
                            </>
                          ) : (
                            <div className="text-center text-gray-300 text-xs">-</div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ---------------- Periods per week for each teacher */}
      {tab === 'load' && (
        <div className="print-area card">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Teachers' Load</h2>
          <p className="text-sm text-gray-500 mb-4">Periods per week for each teacher in the draft.</p>
          {draft.teacher_load.length === 0 ? (
            <p className="text-sm text-gray-500">No periods with a teacher yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Teacher</th>
                    <th>Periods per week</th>
                  </tr>
                </thead>
                <tbody>
                  {draft.teacher_load.map((teacher) => (
                    <tr key={teacher.teacher_id}>
                      <td className="font-semibold">{teacher.teacher_name}</td>
                      <td>{teacher.periods}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Publish window */}
      <Modal isOpen={isPublishOpen} onClose={() => setIsPublishOpen(false)} title="Publish the timetable">
        <div className="space-y-3 text-sm">
          {publishErrors.length > 0 ? (
            <>
              <div className="p-3 rounded-lg bg-red-50 text-red-800">
                <div className="font-semibold flex items-center gap-1 mb-1"><AlertTriangle size={16} /> Fix these clashes first:</div>
                <ul className="list-disc ml-5 space-y-1">
                  {publishErrors.map((text) => <li key={text}>{text}</li>)}
                </ul>
              </div>
              <div className="flex justify-end">
                <button onClick={() => setIsPublishOpen(false)} className="btn btn-secondary">Close</button>
              </div>
            </>
          ) : (
            <>
              <p className="text-gray-700">
                Every teacher will see their own periods and every student will see their section's timetable on their Timetable page.
              </p>
              {publishWarnings.length > 0 ? (
                <div className="p-3 rounded-lg bg-yellow-50 text-yellow-800">
                  <div className="font-semibold flex items-center gap-1 mb-1"><AlertTriangle size={16} /> Worth checking (you can still publish):</div>
                  <ul className="list-disc ml-5 space-y-1">
                    {publishWarnings.map((text) => <li key={text}>{text}</li>)}
                  </ul>
                </div>
              ) : (
                <div className="p-3 rounded-lg bg-green-50 text-green-800 flex items-center gap-1"><CheckCircle2 size={16} /> Everything looks good.</div>
              )}
              <div className="flex justify-end gap-2">
                <button onClick={() => setIsPublishOpen(false)} className="btn btn-secondary">Cancel</button>
                <button onClick={handlePublish} className="btn btn-primary flex items-center gap-2"><Send size={16} /> Publish now</button>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* Empty a section's timetable */}
      <Modal isOpen={isClearOpen} onClose={() => setIsClearOpen(false)} title="Empty this timetable">
        <p className="text-sm text-gray-700">Remove every period from {selectedSection?.section_name}'s draft timetable? Teachers and students keep seeing the published one until you publish again.</p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setIsClearOpen(false)} className="btn btn-secondary">Cancel</button>
          <button onClick={handleClear} className="btn btn-primary bg-red-600 hover:bg-red-700">Empty it</button>
        </div>
      </Modal>

      {/* Bell schedule and school days */}
      <Modal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} title="Bell schedule and school days">
        <div className="space-y-4 text-sm">
          <div>
            <div className="font-medium text-gray-700 mb-2">School days</div>
            <div className="flex flex-wrap gap-2">
              {ALL_DAYS.map((day) => (
                <label key={day.day} className="flex items-center gap-1">
                  <input type="checkbox" checked={schoolDays.includes(day.day)} onChange={() => toggleDay(day.day)} />
                  {day.name}
                </label>
              ))}
            </div>
          </div>
          <div>
            <div className="font-medium text-gray-700 mb-2">Periods and breaks</div>
            <div className="space-y-2 max-h-72 overflow-y-auto">
              {bellRows.map((row, index) => (
                <div key={index} className="flex flex-wrap items-center gap-2">
                  <input type="text" value={row.name} onChange={(e) => changeBellRow(index, 'name', e.target.value)} className="input py-1 w-28" />
                  <input type="time" value={row.start_time} onChange={(e) => changeBellRow(index, 'start_time', e.target.value)} className="input py-1 w-28" />
                  <span>to</span>
                  <input type="time" value={row.end_time} onChange={(e) => changeBellRow(index, 'end_time', e.target.value)} className="input py-1 w-28" />
                  <label className="flex items-center gap-1 text-xs">
                    <input type="checkbox" checked={row.is_break} onChange={(e) => changeBellRow(index, 'is_break', e.target.checked)} /> Break
                  </label>
                  <button onClick={() => removeBellRow(index)} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Remove"><Trash2 size={14} /></button>
                </div>
              ))}
            </div>
            <div className="flex gap-2 mt-2">
              <button onClick={() => addBellRow(false)} className="btn btn-secondary text-xs flex items-center gap-1"><Plus size={14} /> Add Period</button>
              <button onClick={() => addBellRow(true)} className="btn btn-secondary text-xs flex items-center gap-1"><Plus size={14} /> Add Break</button>
            </div>
            <p className="text-xs text-gray-500 mt-2">Periods are numbered by their start time. If you remove days or periods, the draft periods on them are removed too.</p>
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setIsSettingsOpen(false)} className="btn btn-secondary">Cancel</button>
            <button onClick={handleSaveSettings} className="btn btn-primary">Save</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AdminTimetable;
