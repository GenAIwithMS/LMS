import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, getSections } from '../../services/api';
import type { Announcement, Section } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

const TeacherAnnouncements: React.FC = () => {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingAnnouncement, setDeletingAnnouncement] = useState<Announcement | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterSection, setFilterSection] = useState('all');
  const [filterAudience, setFilterAudience] = useState('all');
  const optionsRef = useRef<HTMLDivElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    target_audience: 'all',
    section_name: '',
  });

  useEffect(() => {
    fetchAnnouncements();
    fetchSections();
  }, []);

  // Close options dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (optionsRef.current && !optionsRef.current.contains(event.target as Node)) {
        setShowOptions(false);
      }
    };

    if (showOptions) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showOptions]);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      const data = await getAnnouncements();
      setAnnouncements(Array.isArray(data) ? data : data.announcement ? [data.announcement] : []);
    } catch (error: any) {
      showError(error, 'Failed to fetch announcements');
    } finally {
      setLoading(false);
    }
  };

  const fetchSections = async () => {
    try {
      const data = await getSections();
      setSections(Array.isArray(data) ? data : data.section ? [data.section] : []);
    } catch (error) {
      console.error('Failed to fetch sections');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAnnouncement) {
        await updateAnnouncement(editingAnnouncement.id, formData);
        showSuccess('Announcement updated successfully');
      } else {
        await createAnnouncement(formData);
        showSuccess('Announcement created successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchAnnouncements();
    } catch (error: any) {
      showError(error, 'Failed to save announcement');
    }
  };

  const handleEdit = (announcement: Announcement) => {
    setEditingAnnouncement(announcement);
    setFormData({
      title: announcement.title,
      content: announcement.content,
      target_audience: announcement.target_audience,
      section_name: announcement.section,
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (announcement: Announcement) => {
    setDeletingAnnouncement(announcement);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingAnnouncement) return;
    
    setIsDeleting(true);
    try {
      await deleteAnnouncement(deletingAnnouncement.id);
      showSuccess('Announcement deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingAnnouncement(null);
      fetchAnnouncements();
    } catch (error: any) {
      showError(error, 'Failed to delete announcement');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ title: '', content: '', target_audience: 'all', section_name: '' });
    setEditingAnnouncement(null);
  };

  const filteredAnnouncements = announcements
    .filter((announcement) => {
      const title = announcement.title?.toLowerCase() || '';
      const content = announcement.content?.toLowerCase() || '';
      const search = searchTerm.toLowerCase();
      const matchesSearch = title.includes(search) || content.includes(search);
      const matchesSection = filterSection === 'all' || announcement.section === filterSection;
      const matchesAudience = filterAudience === 'all' || announcement.target_audience === filterAudience;
      return matchesSearch && matchesSection && matchesAudience;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'title':
          aValue = (a.title || '').toLowerCase();
          bValue = (b.title || '').toLowerCase();
          break;
        case 'section':
          aValue = (a.section || '').toLowerCase();
          bValue = (b.section || '').toLowerCase();
          break;
        case 'target_audience':
          aValue = (a.target_audience || '').toLowerCase();
          bValue = (b.target_audience || '').toLowerCase();
          break;
        default:
          aValue = a.id || 0;
          bValue = b.id || 0;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Announcements</h1>
          <p className="text-gray-600 mt-2">Create and manage announcements</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Search Bar with Options Icon */}
          <div className="relative" ref={optionsRef}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 pr-10 py-2 text-sm w-[250px] transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <button
                onClick={() => setShowOptions(!showOptions)}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded transition-all duration-200"
                title="Sort & Filter Options"
              >
                <Settings size={16} />
              </button>
            </div>

            {/* Options Dropdown */}
            {showOptions && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50 p-4 transition-all duration-200 transform origin-top-right opacity-100 scale-100">
                <div className="space-y-4">
                  {/* Sort Section */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="id">ID</option>
                      <option value="title">Title</option>
                      <option value="section">Section</option>
                      <option value="target_audience">Target Audience</option>
                    </select>
                    <div className="mt-2">
                      <button
                        onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                        className="btn btn-secondary text-sm px-3 py-1.5 w-full transition-all duration-200 hover:scale-105"
                      >
                        {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
                      </button>
                    </div>
                  </div>

                  {/* Filter Section */}
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Section</label>
                      <select
                        value={filterSection}
                        onChange={(e) => setFilterSection(e.target.value)}
                        className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="all">All Sections</option>
                        {sections.map((section) => (
                          <option key={section.id} value={section.name}>
                            {section.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Audience</label>
                      <select
                        value={filterAudience}
                        onChange={(e) => setFilterAudience(e.target.value)}
                        className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="all">All Audiences</option>
                        <option value="all">All</option>
                        <option value="students">Students</option>
                        <option value="teachers">Teachers</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button onClick={() => { resetForm(); setIsModalOpen(true); }} className="btn btn-primary flex items-center space-x-2">
            <Plus size={20} />
            <span>Create Announcement</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredAnnouncements.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No announcements found</div>
        ) : (
          filteredAnnouncements.map((announcement) => (
            <div key={announcement.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{announcement.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{announcement.teacher} • {announcement.section}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button onClick={() => handleEdit(announcement)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                    <Edit size={18} />
                  </button>
                  <button onClick={() => handleDelete(announcement.id)} className="p-2 text-red-600 hover:bg-red-50 rounded">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              <p className="text-gray-600 mb-4">{announcement.content}</p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{new Date(announcement.created_at).toLocaleDateString()}</span>
                <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs">{announcement.target_audience}</span>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingAnnouncement ? 'Edit Announcement' : 'Create Announcement'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Content</label>
            <textarea required value={formData.content} onChange={(e) => setFormData({ ...formData, content: e.target.value })} className="input" rows={5} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Target Audience</label>
            <select required value={formData.target_audience} onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })} className="input">
              <option value="all">All</option>
              <option value="students">Students</option>
              <option value="teachers">Teachers</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Section</label>
            <select required value={formData.section_name} onChange={(e) => setFormData({ ...formData, section_name: e.target.value })} className="input">
              <option value="">Select a section</option>
              {sections.map((section) => (
                <option key={section.id} value={section.name}>{section.name}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingAnnouncement ? 'Update' : 'Create'} Announcement</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingAnnouncement(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Announcement"
        itemName={deletingAnnouncement?.title || ''}
        itemType="announcement"
        effects={[
          'This announcement will be permanently removed',
          'All notifications related to this announcement will be deleted',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default TeacherAnnouncements;

