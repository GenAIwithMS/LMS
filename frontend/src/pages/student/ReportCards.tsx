import React, { useState, useEffect } from 'react';
import { FileText, Printer } from 'lucide-react';
import { getExamTerms, getReportCard } from '../../services/api';
import type { ExamTerm, ReportCard } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import { ReportCardView } from '../../components/ReportCardView';
import { showError } from '../../utils/errorHandler';

// A student's report cards: choose a term (only published ones are listed)
// to see the report card, and print it.
const StudentReportCards: React.FC = () => {
  const { user } = useAuth();
  const [terms, setTerms] = useState<ExamTerm[]>([]);
  const [selectedTermId, setSelectedTermId] = useState<number | null>(null);
  const [card, setCard] = useState<ReportCard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTerms = async () => {
      try {
        const data = await getExamTerms();
        const termList: ExamTerm[] = Array.isArray(data) ? data : [];
        setTerms(termList);
        // Open the newest report card straight away
        if (termList.length > 0) {
          setSelectedTermId(termList[0].id);
        }
      } catch (error: any) {
        showError(error, 'Failed to load your report cards');
      } finally {
        setLoading(false);
      }
    };
    fetchTerms();
  }, []);

  useEffect(() => {
    const fetchCard = async () => {
      if (selectedTermId === null || !user) return;
      try {
        setCard(null);
        const data = await getReportCard(selectedTermId, user.id);
        setCard(data);
      } catch (error: any) {
        showError(error, 'Failed to load the report card');
      }
    };
    fetchCard();
  }, [selectedTermId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="no-print">
        <h1 className="text-3xl font-bold text-gray-900">Report Card</h1>
        <p className="text-gray-600 mt-2">Your exam results, published by the school</p>
      </div>

      {terms.length === 0 ? (
        <div className="card flex items-center gap-3 text-gray-600">
          <FileText size={24} className="text-gray-400" />
          No results have been published yet.
        </div>
      ) : (
        <>
          <div className="no-print flex flex-wrap items-center gap-3">
            <label className="text-sm text-gray-600">Exam</label>
            <select value={selectedTermId !== null ? String(selectedTermId) : ''} onChange={(e) => setSelectedTermId(Number(e.target.value))} className="input max-w-xs">
              {terms.map((term) => (
                <option key={term.id} value={term.id}>{term.name} ({term.session_name})</option>
              ))}
            </select>
            {card && (
              <button onClick={() => window.print()} className="btn btn-primary flex items-center gap-2">
                <Printer size={16} /> Print
              </button>
            )}
          </div>

          {card ? (
            <ReportCardView card={card} />
          ) : (
            <p className="text-sm text-gray-400">Loading the report card...</p>
          )}
        </>
      )}
    </div>
  );
};

export default StudentReportCards;
