import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer } from 'lucide-react';
import { getReportCard } from '../services/api';
import type { ReportCard } from '../types';
import { ReportCardView } from '../components/ReportCardView';
import { showError } from '../utils/errorHandler';

// One student's report card for one term, with a Print button.
// The admin, the student's teachers, and the student (once published) can open it.
const ReportCardPage: React.FC = () => {
  const { termId, studentId } = useParams();
  const navigate = useNavigate();
  const [card, setCard] = useState<ReportCard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCard = async () => {
      try {
        const data = await getReportCard(Number(termId), Number(studentId));
        setCard(data);
      } catch (error: any) {
        showError(error, 'Failed to load the report card');
      } finally {
        setLoading(false);
      }
    };
    fetchCard();
  }, [termId, studentId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-w-4xl">
      <div className="no-print flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1">
          <ArrowLeft size={16} /> Back
        </button>
        {card && (
          <button onClick={() => window.print()} className="btn btn-primary flex items-center gap-2">
            <Printer size={16} /> Print
          </button>
        )}
      </div>
      {card ? (
        <ReportCardView card={card} />
      ) : (
        <div className="card text-gray-500">This report card can't be shown.</div>
      )}
    </div>
  );
};

export default ReportCardPage;
