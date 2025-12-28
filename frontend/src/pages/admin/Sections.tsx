import React, { useState, useEffect, useRef } from 'react';
import { Plus, Edit, Trash2, Search, Settings } from 'lucide-react';
import { Modal } from '../../components/Modal';
import { DeleteConfirmation } from '../../components/DeleteConfirmation';
import { getSections, addSection, updateSection, deleteSection, getTeachers } from '../../services/api';
import type { Section, Teacher } from '../../types';
import { showError, showSuccess } from '../../utils/errorHandler';
import toast from 'react-hot-toast';

const AdminSections: React.FC = () => {
  const [sections, setSections] = useState<Section[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSection, setEditingSection] = useState<Section | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [filterTeacher, setFilterTeacher] = useState<string>('all');
  const [showOptions, setShowOptions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingSection, setDeletingSection] = useState<Section | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const optionsRef = useRef<HTMLDivElement>(null);
  const [formData, setFormData] = useState({ name: '', teacher_name: '' });

  useEffect(() => {
    fetchSections();
    fetchTeachers();
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

  const fetchSections = async () => {
    try {
      setLoading(true);
      const data = await getSections();
      console.log('Sections API response:', data);
      
      // Handle different response formats
      let sectionsData: Section[] = [];
      
      if (Array.isArray(data)) {
        sectionsData = data;
      } else if (data && Array.isArray(data.sections)) {
        sectionsData = data.sections;
      } else if (data && data.section) {
        sectionsData = Array.isArray(data.section) ? data.section : [data.section];
      } else if (data && typeof data === 'object') {
        const sectionsArray = Object.values(data).find((val) => Array.isArray(val)) as Section[] | undefined;
        if (sectionsArray) {
          sectionsData = sectionsArray;
        }
      }
      
      // Ensure all sections have required fields with proper teacher mapping
      sectionsData = sectionsData.map((section: any) => ({
        id: section.id || 0,
        name: section.name || '',
        teacher: section.teacher || section.teacher_name || '',
      }));
      
      console.log('Processed sections:', sectionsData);
      setSections(sectionsData);
    } catch (error: any) {
      console.error('Error fetching sections:', error);
      showError(error, 'Failed to fetch sections');
      setSections([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTeachers = async () => {
    try {
      const data = await getTeachers();
      setTeachers(Array.isArray(data) ? data : data.teacher ? [data.teacher] : []);
    } catch (error) {
      console.error('Failed to fetch teachers');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingSection) {
        await updateSection(editingSection.id, formData);
        showSuccess('Section updated successfully');
      } else {
        await addSection(formData);
        showSuccess('Section added successfully');
      }
      setIsModalOpen(false);
      resetForm();
      fetchSections();
    } catch (error: any) {
      showError(error, 'Failed to save section');
    }
  };

  const handleEdit = (section: Section) => {
    setEditingSection(section);
    setFormData({ name: section.name, teacher_name: section.teacher });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (section: Section) => {
    setDeletingSection(section);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingSection) return;
    
    setIsDeleting(true);
    try {
      await deleteSection(deletingSection.id);
      showSuccess('Section deleted successfully');
      setShowDeleteConfirm(false);
      setDeletingSection(null);
      fetchSections();
    } catch (error: any) {
      showError(error, 'Failed to delete section');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({ name: '', teacher_name: '' });
    setEditingSection(null);
  };

  const filteredSections = sections
    .filter((section) => {
      const matchesSearch =
        section.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        section.teacher?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTeacher = filterTeacher === 'all' || section.teacher === filterTeacher;
      return matchesSearch && matchesTeacher;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortBy) {
        case 'name':
          aValue = (a.name || '').toLowerCase();
          bValue = (b.name || '').toLowerCase();
          break;
        case 'teacher':
          aValue = (a.teacher || '').toLowerCase();
          bValue = (b.teacher || '').toLowerCase();
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
    <div className="pl-2">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sections</h1>
          <p className="text-gray-600 mt-2">Manage all sections in the system</p>
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
                      <option value="name">Name</option>
                      <option value="teacher">Teacher</option>
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
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Filter By Teacher</label>
                    <select
                      value={filterTeacher}
                      onChange={(e) => setFilterTeacher(e.target.value)}
                      className="input text-sm py-2 px-3 w-full transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="all">All Teachers</option>
                      {teachers.map((teacher) => (
                        <option key={teacher.id} value={teacher.name}>
                          {teacher.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button onClick={() => { resetForm(); setIsModalOpen(true); }} className="btn btn-primary flex items-center space-x-2">
            <Plus size={20} />
            <span>Add Section</span>
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Teacher</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredSections.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-8 text-gray-500">No sections found</td>
              </tr>
            ) : (
              filteredSections.map((section) => (
                <tr key={section.id}>
                  <td>{section.id}</td>
                  <td>{section.name}</td>
                  <td>{section.teacher}</td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <button onClick={() => handleEdit(section)} className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                        <Edit size={18} />
                      </button>
                      <button onClick={() => handleDeleteClick(section)} className="p-2 text-red-600 hover:bg-red-50 rounded">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); resetForm(); }} title={editingSection ? 'Edit Section' : 'Add Section'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input type="text" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Teacher</label>
            <select required value={formData.teacher_name} onChange={(e) => setFormData({ ...formData, teacher_name: e.target.value })} className="input">
              <option value="">Select a teacher</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.name}>{teacher.name}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={() => { setIsModalOpen(false); resetForm(); }} className="btn btn-secondary">Cancel</button>
            <button type="submit" className="btn btn-primary">{editingSection ? 'Update' : 'Add'} Section</button>
          </div>
        </form>
      </Modal>

      <DeleteConfirmation
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setDeletingSection(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Section"
        itemName={deletingSection?.name || ''}
        itemType="section"
        effects={[
          'All students in this section',
          'All enrollments for students in this section',
        ]}
        loading={isDeleting}
      />
    </div>
  );
};

export default AdminSections;

