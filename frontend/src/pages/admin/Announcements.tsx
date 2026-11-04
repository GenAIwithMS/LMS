import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Megaphone, Plus, Edit, Trash2, Search, Users, MapPin } from 'lucide-react';
import { getAnnouncements, getSchoolClasses, createAdminAnnouncement, updateAdminAnnouncement, deleteAnyAnnouncement } from '../../services/api';
import type { Announcement, SchoolClassSummary } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

type Where = 'school' | 'class' | 'section';

interface AnnouncementForm {
  title: string;
  content: string;
  target_audience: string;
  where: Where;
  class_id: string;
  section_id: string;
}

const EMPTY_FORM: AnnouncementForm = {
  title: '',
  content: '',
  target_audience: 'all',
  where: 'school',
  class_id: '',
  section_id: '',
};

const AUDIENCE_COLOURS: Record<string, string> = {
  all: 'bg-blue-100 text-blue-800',
  teachers: 'bg-purple-100 text-purple-800',
  students: 'bg-green-100 text-green-800',
};

// The date and time an announcement was posted, like "4 Nov 2026, 16:39".
// The server keeps Pakistan time but labels it GMT, so read it without changing the time zone.
const postedText = (value: string): string => {
  const date = new Date(value);
  if (isNaN(date.getTime())) {
    return value;
  }
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const hours = String(date.getUTCHours()).padStart(2, '0');
  const minutes = String(date.getUTCMinutes()).padStart(2, '0');
  return `${date.getUTCDate()} ${months[date.getUTCMonth()]} ${date.getUTCFullYear()}, ${hours}:${minutes}`;
};

// The admin's announcements: post to everyone, teachers or students, for the whole school,
// one class or one section. The admin sees every announcement (teachers' too) and can delete any.
const AdminAnnouncements: React.FC = () => {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [classes, setClasses] = useState<SchoolClassSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterAuthor, setFilterAuthor] = useState('all');      // all, admin, teacher
  const [filterAudience, setFilterAudience] = useState('all');  // all, everyone, teachers, students

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState<Announcement | null>(null);
  const [form, setForm] = useState<AnnouncementForm>(EMPTY_FORM);

  const [toDelete, setToDelete] = useState<Announcement | null>(null);

  useEffect(() => {
    fetchAnnouncements();
    fetchClasses();
  }, []);

  // The spinner shows only on the first load, so the page doesn't blank out after each change
  const fetchAnnouncements = async () => {
    try {
      const data = await getAnnouncements();
      setAnnouncements(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load the announcements');
    } finally {
      setLoading(false);
    }
  };

  const fetchClasses = async () => {
    try {
      const data = await getSchoolClasses();
      setClasses(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load the classes');
    }
  };

  // ---------------- The form

  const openNew = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setIsFormOpen(true);
  };

  const openEdit = (announcement: Announcement) => {
    let where: Where = 'school';
    if (announcement.class_id) {
      where = 'class';
    }
    if (announcement.section_id) {
      where = 'section';
    }

    // For a section, also choose its class in the form
    let classId = announcement.class_id ? String(announcement.class_id) : '';
    if (announcement.section_id) {
      for (const schoolClass of classes) {
        for (const section of schoolClass.sections) {
          if (section.id === announcement.section_id) {
            classId = String(schoolClass.id);
          }
        }
      }
    }

    setEditing(announcement);
    setForm({
      title: announcement.title,
      content: announcement.content,
      target_audience: announcement.target_audience,
      where: where,
      class_id: classId,
      section_id: announcement.section_id ? String(announcement.section_id) : '',
    });
    setIsFormOpen(true);
  };

  const changeForm = (field: keyof AnnouncementForm, value: string) => {
    const newForm = { ...form, [field]: value };
    // A new class means its section must be chosen again
    if (field === 'class_id') {
      newForm.section_id = '';
    }
    setForm(newForm);
  };

  // The sections of the class chosen in the form
  let formSections: { id: number; full_name: string }[] = [];
  for (const schoolClass of classes) {
    if (String(schoolClass.id) === form.class_id) {
      formSections = schoolClass.sections;
    }
  }

  let sectionPlaceholder = 'Choose a section';
  if (form.class_id === '') {
    sectionPlaceholder = 'Choose a class first';
  } else if (formSections.length === 0) {
    sectionPlaceholder = 'This class has no sections';
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.title.trim() === '' || form.content.trim() === '') {
      toast.error('Write a title and a message');
      return;
    }

    // Where it goes: nothing for the whole school, a class, or a section
    let classId: number | null = null;
    let sectionId: number | null = null;
    if (form.where === 'class') {
      if (!form.class_id) {
        toast.error('Choose the class');
        return;
      }
      classId = Number(form.class_id);
    }
    if (form.where === 'section') {
      if (!form.section_id) {
        toast.error('Choose the class and section');
        return;
      }
      sectionId = Number(form.section_id);
    }

    const data = {
      title: form.title.trim(),
      content: form.content.trim(),
      target_audience: form.target_audience,
      class_id: classId,
      section_id: sectionId,
    };

    try {
      if (editing) {
        await updateAdminAnnouncement(editing.id, data);
        showSuccess('Announcement updated');
      } else {
        await createAdminAnnouncement(data);
        showSuccess('Announcement posted');
      }
      setIsFormOpen(false);
      fetchAnnouncements();
    } catch (error: any) {
      showError(error, 'Failed to save the announcement');
    }
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await deleteAnyAnnouncement(toDelete.id);
      showSuccess('Announcement deleted');
      setToDelete(null);
      fetchAnnouncements();
    } catch (error: any) {
      showError(error, 'Failed to delete the announcement');
    }
  };

  // ---------------- The list, with search and filters

  const shown: Announcement[] = [];
  for (const announcement of announcements) {
    const text = (announcement.title + ' ' + announcement.content + ' ' + (announcement.author_name || '')).toLowerCase();
    if (searchTerm.trim() !== '' && !text.includes(searchTerm.trim().toLowerCase())) continue;
    if (filterAuthor !== 'all' && announcement.author_role !== filterAuthor) continue;
    if (filterAudience === 'everyone' && announcement.target_audience !== 'all') continue;
    if (filterAudience === 'teachers' && announcement.target_audience !== 'teachers') continue;
    if (filterAudience === 'students' && announcement.target_audience !== 'students') continue;
    shown.push(announcement);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2"><Megaphone size={28} className="text-primary-600" /> Announcements</h1>
          <p className="text-gray-600 mt-2">Post notices to everyone, only teachers or only students, for the whole school, a class or a section. Teachers' announcements are listed here too.</p>
        </div>
        <button onClick={openNew} className="btn btn-primary flex items-center gap-2"><Plus size={18} /> New Announcement</button>
      </div>

      <div className="card flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[12rem]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="input pl-9" />
        </div>
        <select value={filterAuthor} onChange={(e) => setFilterAuthor(e.target.value)} className="input max-w-[12rem]">
          <option value="all">From anyone</option>
          <option value="admin">From the school (admin)</option>
          <option value="teacher">From teachers</option>
        </select>
        <select value={filterAudience} onChange={(e) => setFilterAudience(e.target.value)} className="input max-w-[12rem]">
          <option value="all">Any audience</option>
          <option value="everyone">For everyone</option>
          <option value="teachers">For teachers</option>
          <option value="students">For students</option>
        </select>
      </div>

      {shown.length === 0 ? (
        <div className="card text-gray-500">
          {announcements.length === 0 ? 'No announcements yet. Click "New Announcement" to post one.' : 'No announcements match the search.'}
        </div>
      ) : (
        <div className="space-y-4">
          {shown.map((announcement) => (
            <div key={announcement.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 break-words">{announcement.title}</h3>
                  <p className="text-sm text-gray-500">
                    {announcement.author_name || 'Unknown'} · {announcement.author_role === 'admin' ? 'Admin' : 'Teacher'} · {postedText(announcement.created_at)}
                  </p>
                </div>
                <div className="flex shrink-0">
                  {announcement.author_role === 'admin' && (
                    <button onClick={() => openEdit(announcement)} className="p-2 text-blue-600 hover:bg-blue-50 rounded" title="Edit"><Edit size={18} /></button>
                  )}
                  <button onClick={() => setToDelete(announcement)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete"><Trash2 size={18} /></button>
                </div>
              </div>
              <p className="text-gray-700 mt-3 whitespace-pre-wrap break-words">{announcement.content}</p>
              <div className="flex flex-wrap gap-2 mt-3 text-xs">
                <span className={`px-2 py-1 rounded-full font-medium flex items-center gap-1 ${AUDIENCE_COLOURS[announcement.target_audience] || 'bg-gray-100 text-gray-700'}`}>
                  <Users size={12} /> For {announcement.audience_text || announcement.target_audience}
                </span>
                <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700 font-medium flex items-center gap-1">
                  <MapPin size={12} /> {announcement.where || 'Whole school'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Post or edit */}
      <Modal isOpen={isFormOpen} onClose={() => setIsFormOpen(false)} title={editing ? 'Edit Announcement' : 'New Announcement'}>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input type="text" maxLength={255} value={form.title} onChange={(e) => changeForm('title', e.target.value)} className="input" placeholder="e.g. School closed on Friday" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
            <textarea rows={5} value={form.content} onChange={(e) => changeForm('content', e.target.value)} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Who is it for?</label>
            <div className="flex flex-wrap gap-4 text-sm">
              <label className="flex items-center gap-1"><input type="radio" checked={form.target_audience === 'all'} onChange={() => changeForm('target_audience', 'all')} /> Everyone</label>
              <label className="flex items-center gap-1"><input type="radio" checked={form.target_audience === 'teachers'} onChange={() => changeForm('target_audience', 'teachers')} /> Teachers only</label>
              <label className="flex items-center gap-1"><input type="radio" checked={form.target_audience === 'students'} onChange={() => changeForm('target_audience', 'students')} /> Students only</label>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Where?</label>
            <div className="flex flex-wrap gap-4 text-sm">
              <label className="flex items-center gap-1"><input type="radio" checked={form.where === 'school'} onChange={() => changeForm('where', 'school')} /> Whole school</label>
              <label className="flex items-center gap-1"><input type="radio" checked={form.where === 'class'} onChange={() => changeForm('where', 'class')} /> A class</label>
              <label className="flex items-center gap-1"><input type="radio" checked={form.where === 'section'} onChange={() => changeForm('where', 'section')} /> A section</label>
            </div>
          </div>
          {form.where !== 'school' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select value={form.class_id} onChange={(e) => changeForm('class_id', e.target.value)} className="input">
                <option value="">Choose a class</option>
                {classes.map((schoolClass) => (
                  <option key={schoolClass.id} value={schoolClass.id}>{schoolClass.name}</option>
                ))}
              </select>
              {form.where === 'section' && (
                <select value={form.section_id} onChange={(e) => changeForm('section_id', e.target.value)} className="input" disabled={form.class_id === ''}>
                  <option value="">{sectionPlaceholder}</option>
                  {formSections.map((section) => (
                    <option key={section.id} value={section.id}>{section.full_name}</option>
                  ))}
                </select>
              )}
            </div>
          )}
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setIsFormOpen(false)} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editing ? 'Save' : 'Post'}</button>
          </div>
        </form>
      </Modal>

      {/* Delete */}
      <Modal isOpen={toDelete !== null} onClose={() => setToDelete(null)} title="Delete announcement">
        <p className="text-sm text-gray-700">
          Delete "{toDelete?.title}"{toDelete && toDelete.author_role === 'teacher' ? ` by ${toDelete.author_name}` : ''}? Nobody will see it any more.
        </p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setToDelete(null)} className="btn btn-secondary">Cancel</button>
          <button onClick={handleDelete} className="btn btn-primary bg-red-600 hover:bg-red-700">Delete</button>
        </div>
      </Modal>
    </div>
  );
};

export default AdminAnnouncements;
