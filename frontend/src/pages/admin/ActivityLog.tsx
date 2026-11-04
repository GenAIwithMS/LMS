import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { History, Search, X, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { getActivityLog, getActivityAreas, getSchoolClasses, downloadReport } from '../../services/api';
import type { ActivityFilters } from '../../services/api';
import type { ActivityEntry, SchoolClassSummary } from '../../types';
import { showError } from '../../utils/errorHandler';

const PER_PAGE = 50;

const ACTION_LABELS: Record<string, string> = {
  login: 'Logged in',
  login_failed: 'Failed login',
  logout: 'Logged out',
  create: 'Added',
  update: 'Changed',
  delete: 'Deleted',
};

const ACTION_COLOURS: Record<string, string> = {
  login: 'bg-green-100 text-green-800',
  login_failed: 'bg-red-100 text-red-800',
  logout: 'bg-gray-100 text-gray-700',
  create: 'bg-blue-100 text-blue-800',
  update: 'bg-yellow-100 text-yellow-800',
  delete: 'bg-red-100 text-red-800',
};

const ROLE_COLOURS: Record<string, string> = {
  admin: 'bg-purple-100 text-purple-800',
  teacher: 'bg-blue-100 text-blue-800',
  student: 'bg-green-100 text-green-800',
};

// The filters as typed in the form (all text, so empty boxes are easy to tell apart)
interface FilterForm {
  name: string;
  role: string;
  action: string;
  area: string;
  class_id: string;
  section_id: string;
  date_from: string;
  date_to: string;
}

const EMPTY_FORM: FilterForm = {
  name: '',
  role: '',
  action: '',
  area: '',
  class_id: '',
  section_id: '',
  date_from: '',
  date_to: '',
};

// The activity log: everything people change in the LMS, and every login and logout.
// The admin can filter it by name, role, action, area, class, section and dates.
// Turn the form into the filters sent to the server (empty boxes are left out)
const formToFilters = (values: FilterForm, userId: number | null): ActivityFilters => {
  const result: ActivityFilters = {};
  if (userId !== null) {
    result.user_id = userId;
  } else if (values.name.trim() !== '') {
    result.name = values.name.trim();
  }
  if (values.role) result.role = values.role;
  if (values.action) result.action = values.action;
  if (values.area) result.area = values.area;
  if (values.class_id) result.class_id = Number(values.class_id);
  if (values.section_id) result.section_id = Number(values.section_id);
  if (values.date_from) result.date_from = values.date_from;
  if (values.date_to) result.date_to = values.date_to;
  return result;
};

const AdminActivityLog: React.FC = () => {
  const [searchParams] = useSearchParams();

  // Start with the filters from the address bar, so the very first search already uses them
  const startForm: FilterForm = {
    name: searchParams.get('name') || '',
    role: searchParams.get('role') || '',
    action: searchParams.get('action') || '',
    area: searchParams.get('area') || '',
    class_id: searchParams.get('class_id') || '',
    section_id: searchParams.get('section_id') || '',
    date_from: searchParams.get('date_from') || '',
    date_to: searchParams.get('date_to') || '',
  };
  let startUserId: number | null = null;
  const userIdText = searchParams.get('user_id');
  if (userIdText) {
    startUserId = Number(userIdText);
  }

  const [form, setForm] = useState<FilterForm>(startForm);
  // The filters of the search shown now (the form can change before "Search" is clicked)
  const [filters, setFilters] = useState<ActivityFilters>(() => formToFilters(startForm, startUserId));
  // One person, when the teacher activity page links here (?user_id=..&name=..)
  const [onlyUserId, setOnlyUserId] = useState<number | null>(startUserId);
  const [onlyUserName, setOnlyUserName] = useState(searchParams.get('name') || 'this person');

  const [entries, setEntries] = useState<ActivityEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const [areas, setAreas] = useState<string[]>([]);
  const [classes, setClasses] = useState<SchoolClassSummary[]>([]);

  useEffect(() => {
    fetchLists();
  }, []);

  useEffect(() => {
    fetchLog();
  }, [filters, page]);

  const fetchLists = async () => {
    try {
      const areaData = await getActivityAreas();
      setAreas(Array.isArray(areaData) ? areaData : []);
      const classData = await getSchoolClasses();
      setClasses(Array.isArray(classData) ? classData : []);
    } catch (error: any) {
      showError(error, 'Failed to load the filter lists');
    }
  };

  const fetchLog = async () => {
    try {
      const data = await getActivityLog(filters, page, PER_PAGE);
      setEntries(Array.isArray(data.entries) ? data.entries : []);
      setTotal(data.total || 0);
    } catch (error: any) {
      showError(error, 'Failed to load the activity log');
    } finally {
      setLoading(false);
    }
  };

  const changeForm = (field: keyof FilterForm, value: string) => {
    const newForm = { ...form, [field]: value };
    // A new class means its section must be chosen again
    if (field === 'class_id') {
      newForm.section_id = '';
    }
    setForm(newForm);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setFilters(formToFilters(form, onlyUserId));
  };

  const handleClear = () => {
    setForm(EMPTY_FORM);
    setOnlyUserId(null);
    setOnlyUserName('');
    setPage(1);
    setFilters({});
  };

  const removeOnlyUser = () => {
    setOnlyUserId(null);
    setOnlyUserName('');
    setPage(1);
    setFilters(formToFilters(form, null));
  };

  const handleDownload = async () => {
    try {
      const params: Record<string, string | number | undefined> = { ...filters };
      await downloadReport('activity', params);
    } catch (error: any) {
      showError(error, 'Failed to download the activity log');
    }
  };

  // The sections of the chosen class
  let sectionOptions: { id: number; full_name: string }[] = [];
  for (const schoolClass of classes) {
    if (String(schoolClass.id) === form.class_id) {
      sectionOptions = schoolClass.sections;
    }
  }

  let firstShown = 0;
  if (total > 0) {
    firstShown = (page - 1) * PER_PAGE + 1;
  }
  let lastShown = page * PER_PAGE;
  if (lastShown > total) {
    lastShown = total;
  }
  const hasNext = page * PER_PAGE < total;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2"><History size={28} className="text-primary-600" /> Activity Log</h1>
          <p className="text-gray-600 mt-2">Everything people change in the LMS, and every login and logout. Looking at pages is not recorded.</p>
        </div>
        <button onClick={handleDownload} className="btn btn-secondary flex items-center gap-2">
          <Download size={16} /> Download Excel
        </button>
      </div>

      {/* Filters */}
      <form onSubmit={handleSearch} className="card space-y-4">
        {onlyUserId !== null && (
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 text-primary-700 text-sm">
            Only {onlyUserName}
            <button type="button" onClick={removeOnlyUser} className="hover:text-primary-900" title="Show everyone">
              <X size={14} />
            </button>
          </div>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Name</label>
            <input type="text" value={form.name} onChange={(e) => changeForm('name', e.target.value)} placeholder="Teacher or student name" className="input" disabled={onlyUserId !== null} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Role</label>
            <select value={form.role} onChange={(e) => changeForm('role', e.target.value)} className="input">
              <option value="">All</option>
              <option value="admin">Admin</option>
              <option value="teacher">Teacher</option>
              <option value="student">Student</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Action</label>
            <select value={form.action} onChange={(e) => changeForm('action', e.target.value)} className="input">
              <option value="">All</option>
              <option value="login">Logged in</option>
              <option value="login_failed">Failed login</option>
              <option value="logout">Logged out</option>
              <option value="create">Added</option>
              <option value="update">Changed</option>
              <option value="delete">Deleted</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Area</label>
            <select value={form.area} onChange={(e) => changeForm('area', e.target.value)} className="input">
              <option value="">All</option>
              {areas.map((area) => (
                <option key={area} value={area} className="capitalize">{area}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Class</label>
            <select value={form.class_id} onChange={(e) => changeForm('class_id', e.target.value)} className="input">
              <option value="">All</option>
              {classes.map((schoolClass) => (
                <option key={schoolClass.id} value={schoolClass.id}>{schoolClass.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Section</label>
            <select value={form.section_id} onChange={(e) => changeForm('section_id', e.target.value)} className="input" disabled={form.class_id === ''}>
              <option value="">All</option>
              {sectionOptions.map((section) => (
                <option key={section.id} value={section.id}>{section.full_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">From</label>
            <input type="date" value={form.date_from} onChange={(e) => changeForm('date_from', e.target.value)} className="input" />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">To</label>
            <input type="date" value={form.date_to} onChange={(e) => changeForm('date_to', e.target.value)} className="input" />
          </div>
        </div>
        <div className="flex gap-2">
          <button type="submit" className="btn btn-primary flex items-center gap-2"><Search size={16} /> Search</button>
          <button type="button" onClick={handleClear} className="btn btn-secondary">Clear</button>
        </div>
      </form>

      {/* Results */}
      <div className="card">
        {entries.length === 0 ? (
          <p className="text-sm text-gray-500">Nothing matches these filters.</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="table text-sm">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Name</th>
                    <th>Action</th>
                    <th>What</th>
                    <th>Area</th>
                    <th>IP</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry) => (
                    <tr key={entry.id}>
                      <td className="whitespace-nowrap">{entry.created_at}</td>
                      <td>
                        <div className="font-medium text-gray-900">{entry.user_name || '-'}</div>
                        {entry.user_role && (
                          <span className={`px-2 py-0.5 rounded-full text-xs capitalize ${ROLE_COLOURS[entry.user_role]}`}>{entry.user_role}</span>
                        )}
                      </td>
                      <td>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap ${ACTION_COLOURS[entry.action]}`}>
                          {ACTION_LABELS[entry.action] || entry.action}
                        </span>
                      </td>
                      <td>{entry.description}</td>
                      <td className="capitalize">{entry.area}</td>
                      <td className="text-gray-500">{entry.ip_address || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-3 mt-4">
              <span className="text-sm text-gray-600">Showing {firstShown}–{lastShown} of {total}</span>
              <div className="flex gap-2">
                <button onClick={() => setPage(page - 1)} disabled={page === 1} className="btn btn-secondary flex items-center gap-1 disabled:opacity-50">
                  <ChevronLeft size={16} /> Previous
                </button>
                <button onClick={() => setPage(page + 1)} disabled={!hasNext} className="btn btn-secondary flex items-center gap-1 disabled:opacity-50">
                  Next <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AdminActivityLog;
