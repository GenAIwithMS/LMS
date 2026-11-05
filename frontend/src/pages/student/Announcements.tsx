import React, { useState, useEffect } from 'react';
import { Search, Bell, Calendar } from 'lucide-react';
import { getAnnouncements } from '../../services/api';
import type { Announcement } from '../../types';
import { announcementLook } from '../../utils/announcementLook';
import toast from 'react-hot-toast';

// "5 Nov 2026": the day first, as dates are read in Pakistan
const dateText = (value: string | null | undefined): string => {
  if (!value) {
    return '-';
  }
  const date = new Date(value);
  if (isNaN(date.getTime())) {
    return value;
  }
  // The server's time is already Pakistan time (labelled GMT), so read its GMT parts as they are
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
};

const StudentAnnouncements: React.FC = () => {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      const data = await getAnnouncements();
      let list: any[] = [];
      if (Array.isArray(data)) {
        list = data;
      } else if (data.announcement) {
        list = [data.announcement];
      }
      // The page shows who wrote it ("Principal (Admin)" for the admin) and where it goes
      const announcementsData: Announcement[] = [];
      for (const announcement of list) {
        // "Principal (Admin)", "Sara Ahmed (Class incharge of Class 5 - A)" or "Omar Malik (Teacher)"
        let author = announcement.author_text || announcement.author_name || announcement.teacher_name || '';
        announcementsData.push({
          ...announcement,
          section: announcement.where || announcement.section_name || '',
          section_id: announcement.section_id,
          teacher: author,
        });
      }
      setAnnouncements(announcementsData);
    } catch (error) {
      toast.error('Failed to fetch announcements');
    } finally {
      setLoading(false);
    }
  };

  const filteredAnnouncements = announcements.filter((announcement) =>
    announcement.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    announcement.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      {/* On a phone the title and the search box stack, so nothing is pushed off the screen */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Announcements</h1>
          <p className="text-gray-600 mt-2">Stay updated with latest announcements</p>
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Search Bar */}
          <div className="relative w-full sm:w-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 pr-10 py-2 text-sm w-full sm:w-[250px] transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredAnnouncements.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No announcements found</div>
        ) : (
          filteredAnnouncements.map((announcement) => (
            <div key={announcement.id} className={`card ${announcementLook(announcement).cardClass}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <Bell className="text-primary-600" size={20} />
                    <h3 className="text-lg font-semibold text-gray-900">{announcement.title}</h3>
                    {announcementLook(announcement).badgeText && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${announcementLook(announcement).badgeClass}`}>{announcementLook(announcement).badgeText}</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{announcement.teacher} • {announcement.section}</p>
                </div>
                <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs">
                  {announcement.audience_text || announcement.target_audience}
                </span>
              </div>
              <p className="text-gray-600 mb-4">{announcement.content}</p>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Calendar size={16} />
                <span>{dateText(announcement.created_at)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default StudentAnnouncements;

