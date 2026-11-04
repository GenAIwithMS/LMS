import type { Announcement } from '../types';

// How an announcement looks, so the same kind has the same colour on every page:
// - from the class incharge (a class announcement): amber
// - from the school (the admin): indigo
// - from a subject teacher: the normal look
export interface AnnouncementLook {
  cardClass: string;         // extra classes for the card (a coloured left border and background)
  badgeText: string | null;  // a small label, or null for none
  badgeClass: string;
}

export const announcementLook = (announcement: Announcement): AnnouncementLook => {
  if (announcement.from_incharge) {
    return {
      cardClass: 'border-l-4 border-l-amber-500 bg-amber-50',
      badgeText: 'Class Incharge',
      badgeClass: 'bg-amber-100 text-amber-800',
    };
  }
  if (announcement.author_role === 'admin') {
    return {
      cardClass: 'border-l-4 border-l-indigo-500',
      badgeText: 'School',
      badgeClass: 'bg-indigo-100 text-indigo-800',
    };
  }
  return {
    cardClass: '',
    badgeText: null,
    badgeClass: '',
  };
};
