import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Clock,
  FileText,
  TrendingUp,
  Bell,
  MessageSquare,
  CalendarDays,
  BookOpen,
  ArrowRight,
  Menu,
  X,
} from 'lucide-react';
import Crest from '../components/Crest';

// The public front page of The Lyceum: what the system does, for whom, and how it is kept safe.

// A few rows of a register, drawn in HTML to show what the attendance page looks like.
// The names are made up (labelled "Sample" on the page).
const SAMPLE_REGISTER = [
  { name: 'Ayesha Khan', marks: ['P', 'P', 'P', 'L', 'P'] },
  { name: 'Bilal Ahmed', marks: ['P', 'A', 'P', 'P', 'P'] },
  { name: 'Fatima Noor', marks: ['P', 'P', 'P', 'P', 'P'] },
  { name: 'Hamza Raza', marks: ['P', 'P', 'A', 'P', 'P'] },
  { name: 'Zainab Ali', marks: ['P', 'P', 'P', 'P', 'L'] },
];
const SAMPLE_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

const markLook = (mark: string): string => {
  if (mark === 'A') {
    return 'text-red-700 font-semibold';
  }
  if (mark === 'L') {
    return 'text-brass-600 font-semibold';
  }
  return 'text-gray-500';
};

const Homepage: React.FC = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    {
      icon: Clock,
      title: 'Daily attendance',
      description: 'The class incharge marks the register each morning, and the office sees who is absent the same day.',
    },
    {
      icon: CalendarDays,
      title: 'Timetable',
      description: 'The office builds each section’s week period by period, and no teacher is booked in two rooms at once.',
    },
    {
      icon: BookOpen,
      title: 'Syllabus and daily topics',
      description: 'Teachers write the chapters for each section and tick topics off as they teach them.',
    },
    {
      icon: FileText,
      title: 'Assignments and class tests',
      description: 'Set work with a due date, collect submissions and enter marks in one place.',
    },
    {
      icon: TrendingUp,
      title: 'Exams and report cards',
      description: 'Term marks become printable report cards, using the school’s own grading scale.',
    },
    {
      icon: Bell,
      title: 'Announcements and events',
      description: 'Notices from the office or a class teacher, and a calendar of holidays and school days.',
    },
    {
      icon: MessageSquare,
      title: 'Assistant',
      description: 'Ask questions in plain words and get answers from the school’s own records.',
    },
  ];

  const roles = [
    {
      title: 'The office',
      features: ['Adds students and teachers', 'Sets up classes, sections and subjects', 'Builds and publishes the timetable', 'Runs exam terms and promotion'],
    },
    {
      title: 'Teachers',
      features: ['Marks attendance', 'Writes the syllabus and daily topics', 'Sets assignments and class tests', 'Enters exam marks'],
    },
    {
      title: 'Students',
      features: ['Sees homework and due dates', 'Hands in assignments', 'Checks marks and attendance', 'Reads their report card'],
    },
  ];

  const safeguards = [
    { title: 'Accounts made by the school', text: 'There is no public sign-up. The office creates every login.' },
    { title: 'Each role sees its own records', text: 'A student sees only their own marks; a teacher only the classes they teach.' },
    { title: 'Wrong passwords pause the account', text: 'After repeated wrong passwords, that account’s login is paused for a while.' },
    { title: 'Sessions end on their own', text: 'A login expires after a set time, and leaving the site signs you out.' },
  ];

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  const currentYear = new Date().getFullYear();

  return (
    <div className="min-h-screen bg-paper text-gray-900">
      {/* Top bar */}
      <nav className="sticky top-0 z-50 bg-paper/95 border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2.5">
              <Crest size={32} />
              <span className="font-serif text-xl font-semibold tracking-tight">The Lyceum</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <button onClick={() => scrollTo('features')} className="text-sm text-gray-700 hover:text-gray-900">What it does</button>
              <button onClick={() => scrollTo('roles')} className="text-sm text-gray-700 hover:text-gray-900">Who uses it</button>
              <button onClick={() => scrollTo('security')} className="text-sm text-gray-700 hover:text-gray-900">Safety</button>
              <button onClick={() => navigate('/login')} className="btn btn-primary text-sm py-1.5">Sign in</button>
            </div>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 -mr-2 text-gray-700"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
          {mobileMenuOpen && (
            <div className="md:hidden py-3 border-t border-gray-200">
              <button onClick={() => scrollTo('features')} className="block w-full text-left py-2.5 text-gray-800">What it does</button>
              <button onClick={() => scrollTo('roles')} className="block w-full text-left py-2.5 text-gray-800">Who uses it</button>
              <button onClick={() => scrollTo('security')} className="block w-full text-left py-2.5 text-gray-800">Safety</button>
              <button onClick={() => navigate('/login')} className="block w-full text-left py-2.5 font-semibold text-primary-700">Sign in</button>
            </div>
          )}
        </div>
      </nav>

      {/* Opening */}
      <header className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-16 sm:pt-20 sm:pb-24 grid lg:grid-cols-[1.1fr_1fr] gap-12 lg:gap-16 items-center">
        <div>
          <p className="text-sm font-semibold text-brass-600">School management for Classes 1 to 10</p>
          <h1 className="mt-4 text-[2.6rem] sm:text-6xl leading-[1.05] font-semibold text-gray-900">
            The school’s register, open to everyone who keeps it.
          </h1>
          <p className="mt-6 text-lg text-gray-700 max-w-xl leading-relaxed">
            Attendance, the timetable, the syllabus, homework, tests and report cards, kept in one place by the office,
            the teachers and the students themselves.
          </p>
          <div className="mt-9 flex flex-col sm:flex-row gap-3">
            <button onClick={() => navigate('/login')} className="btn btn-primary px-6 py-3 inline-flex items-center justify-center gap-2">
              Sign in to The Lyceum
              <ArrowRight size={18} />
            </button>
            <button onClick={() => scrollTo('features')} className="btn btn-secondary px-6 py-3">
              See what it does
            </button>
          </div>
          <p className="mt-5 text-sm text-gray-500">Only for accounts made by the school office.</p>
        </div>

        {/* A sample register page */}
        <figure className="bg-white border border-gray-300 rounded-lg shadow-[0_1px_0_#e3e0d8,0_12px_32px_-16px_rgba(28,27,24,0.3)] overflow-hidden">
          <div className="flex items-baseline justify-between px-5 pt-4 pb-3 border-b-[3px] border-double border-gray-300">
            <div>
              <p className="font-serif text-lg font-semibold">Class 5 – A</p>
              <p className="text-xs text-gray-500">Attendance register · week 3</p>
            </div>
            <span className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 border border-gray-300 rounded px-1.5 py-0.5">Sample</span>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs">
                <th className="text-left font-medium px-5 py-2">Student</th>
                {SAMPLE_DAYS.map((day) => (
                  <th key={day} className="font-medium px-2 py-2 w-11 text-center">{day}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SAMPLE_REGISTER.map((row) => (
                <tr key={row.name} className="border-t border-gray-200">
                  <td className="px-5 py-2.5 text-gray-900">{row.name}</td>
                  {row.marks.map((mark, index) => (
                    <td key={index} className={`text-center py-2.5 ${markLook(mark)}`}>{mark}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <figcaption className="px-5 py-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-600">
            P present · A absent · L leave
          </figcaption>
        </figure>
      </header>

      {/* Why */}
      <section className="border-y border-gray-200 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid md:grid-cols-[1fr_1.4fr] gap-8 md:gap-16">
          <h2 className="font-serif text-3xl font-semibold leading-tight">One record, not a shelf of notebooks.</h2>
          <div className="space-y-4 text-gray-700 leading-relaxed">
            <p>
              Most schools keep attendance in one notebook, marks in a spreadsheet, the timetable on a wall chart and
              notices on WhatsApp. Nothing agrees with anything else, and the office copies the same names again and again.
            </p>
            <p>
              The Lyceum keeps them together. A student added once appears in their section’s register, timetable, tests and
              report card, and every teacher sees the same up-to-date record.
            </p>
          </div>
        </div>
      </section>

      {/* What it does */}
      <section id="features" className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 scroll-mt-16">
        <h2 className="font-serif text-3xl sm:text-4xl font-semibold">What it does</h2>
        <div className="mt-10 grid md:grid-cols-2 gap-x-16 border-t border-gray-300">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div key={feature.title} className="flex gap-4 py-6 border-b border-gray-200">
                <Icon size={20} className="text-primary-600 mt-0.5 shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900">{feature.title}</h3>
                  <p className="mt-1 text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Who uses it */}
      <section id="roles" className="bg-primary-800 text-primary-100 scroll-mt-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-white">Who uses it</h2>
          <p className="mt-3 text-primary-200 max-w-xl">Everyone logs in to the same school, and each sees the part that is theirs.</p>
          <div className="mt-10 grid md:grid-cols-3 md:divide-x divide-white/15 border-t border-white/15">
            {roles.map((role) => (
              <div key={role.title} className="py-8 md:px-8 first:md:pl-0 border-b border-white/15 md:border-b-0">
                <h3 className="font-serif text-2xl font-semibold text-white">{role.title}</h3>
                <ul className="mt-5 space-y-2.5">
                  {role.features.map((feature) => (
                    <li key={feature} className="flex gap-3">
                      <span className="mt-[0.6rem] h-px w-3 bg-brass-500 shrink-0" aria-hidden="true"></span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Safety */}
      <section id="security" className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 scroll-mt-16">
        <div className="grid md:grid-cols-[1fr_1.6fr] gap-8 md:gap-16">
          <div>
            <h2 className="font-serif text-3xl sm:text-4xl font-semibold">Keeping records safe</h2>
            <p className="mt-3 text-gray-600">Children’s marks and attendance are private. These are the rules the system enforces.</p>
          </div>
          <dl className="border-t border-gray-300">
            {safeguards.map((item) => (
              <div key={item.title} className="py-5 border-b border-gray-200 sm:grid sm:grid-cols-[14rem_1fr] sm:gap-6">
                <dt className="font-semibold text-gray-900">{item.title}</dt>
                <dd className="mt-1 sm:mt-0 text-gray-600">{item.text}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-300 bg-gray-100">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <Crest size={28} />
            <span className="font-serif text-lg font-semibold">The Lyceum</span>
          </div>
          <div className="text-sm text-gray-600 sm:text-right">
            <p>For the school’s own use.</p>
            <p className="text-gray-500">© {currentYear} The Lyceum</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;
