import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, UserCheck, BookOpen, Users } from 'lucide-react';
import { getClassSection, setSubjectTeacher, getTeachers } from '../services/api';
import type { SectionDetails, Teacher } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { showError, showSuccess } from '../utils/errorHandler';

// One section (for example Class 5 - A): its class incharge, who teaches each subject,
// and its students. The admin can choose the subject teachers; teachers can only look.
const SectionDetail: React.FC = () => {
  const { sectionId } = useParams();
  const navigate = useNavigate();
  const { userRole } = useAuth();
  const isAdmin = userRole === 'admin';

  const [section, setSection] = useState<SectionDetails | null>(null);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSection();
    if (isAdmin) {
      fetchTeachers();
    }
  }, [sectionId]);

  // The spinner shows only on the first load, so the page doesn't blank out after each save.
  const fetchSection = async () => {
    try {
      const data = await getClassSection(Number(sectionId));
      setSection(data);
    } catch (error: any) {
      showError(error, 'Failed to load the section');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeachers = async () => {
    try {
      const data = await getTeachers();
      setTeachers(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load teachers');
    }
  };

  const handleTeacherChange = async (subjectId: number, teacherId: string) => {
    try {
      const data = await setSubjectTeacher(Number(sectionId), subjectId, teacherId ? Number(teacherId) : null);
      showSuccess(data.message || 'Subject teacher updated');
      fetchSection();
    } catch (error: any) {
      showError(error, 'Failed to change the subject teacher');
    }
  };

  if (loading || !section) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  let backPath = '/teacher/classes';
  let backLabel = 'My classes';
  if (isAdmin) {
    backPath = section.class_id ? `/admin/classes/${section.class_id}` : '/admin/classes';
    backLabel = section.class_name || 'Classes';
  }

  return (
    <div className="space-y-8">
      <div>
        <button onClick={() => navigate(backPath)} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1 mb-2">
          <ArrowLeft size={16} /> {backLabel}
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{section.full_name}</h1>
        <p className="text-gray-600 mt-2 flex items-center gap-2">
          <UserCheck size={16} /> Class incharge: <span className="font-semibold">{section.incharge_name || 'not chosen yet'}</span>
        </p>
      </div>

      {/* Subject teachers */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Subject Teachers</h2>
        </div>
        {section.subjects.length === 0 ? (
          <p className="text-sm text-gray-500">This class has no subjects yet. The admin adds them on the class page.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Teacher</th>
                </tr>
              </thead>
              <tbody>
                {section.subjects.map((item) => (
                  <tr key={item.subject_id}>
                    <td className="font-semibold">{item.subject_name}</td>
                    <td>
                      {isAdmin ? (
                        <select value={item.teacher_id ? String(item.teacher_id) : ''} onChange={(e) => handleTeacherChange(item.subject_id, e.target.value)} className="input py-1">
                          <option value="">No teacher yet</option>
                          {teachers.map((teacher) => (
                            <option key={teacher.id} value={teacher.id}>{teacher.name} ({teacher.username})</option>
                          ))}
                        </select>
                      ) : (
                        <span>{item.teacher_name || <span className="text-gray-400">No teacher yet</span>}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Students */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Users size={20} className="text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Students ({section.students.length})</h2>
        </div>
        {section.students.length === 0 ? (
          <p className="text-sm text-gray-500">No students in this section yet. The admin adds them on the Students page.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Roll No.</th>
                  <th>Name</th>
                  <th>Username</th>
                </tr>
              </thead>
              <tbody>
                {section.students.map((student) => (
                  <tr key={student.id}>
                    <td>{student.roll_number || '-'}</td>
                    <td>{student.name}</td>
                    <td>{student.username}</td>
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

export default SectionDetail;
