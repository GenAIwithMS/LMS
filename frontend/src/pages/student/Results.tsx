import React, { useState, useEffect } from 'react';
import { Search, Award, TrendingUp } from 'lucide-react';
import { getResults } from '../../services/api';
import type { Result } from '../../types';
import toast from 'react-hot-toast';

const StudentResults: React.FC = () => {
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const data = await getResults();
      
      // Handle different response formats
      let resultsData: Result[] = [];
      
      if (Array.isArray(data)) {
        resultsData = data;
      } else if (data && Array.isArray(data.results)) {
        resultsData = data.results;
      } else if (data && data.result) {
        resultsData = Array.isArray(data.result) ? data.result : [data.result];
      } else if (data && typeof data === 'object') {
        // Try to find any array in the response
        const resultsArray = Object.values(data).find((val) => Array.isArray(val)) as Result[] | undefined;
        if (resultsArray) {
          resultsData = resultsArray;
        }
      }
      
      // Ensure all results have required fields with defaults
      resultsData = resultsData.map((result: any) => ({
        id: result.id || 0,
        student: result.student || result.student_name || '',
        subject: result.subject || result.subject_name || '',
        total_marks: result.total_marks || result.totalMarks || 100,
        obtained_marks: result.obtained_marks || result.obtainedMarks || 0,
        exam_type: result.exam_type || result.examType || '',
        remarks: result.remarks || '',
      }));
      
      setResults(resultsData);
    } catch (error: any) {
      console.error('Error fetching results:', error);
      toast.error(error.response?.data?.message || 'Failed to fetch results');
    } finally {
      setLoading(false);
    }
  };

  const filteredResults = results.filter((result) =>
    result.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.exam_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const calculatePercentage = (obtained: number, total: number) => {
    return total > 0 ? ((obtained / total) * 100).toFixed(1) : '0';
  };

  const getGradeColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 80) return 'text-blue-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

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
          <h1 className="text-3xl font-bold text-gray-900">My Results</h1>
          <p className="text-gray-600 mt-2">View your academic results</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 pr-10 py-2 text-sm w-[250px] transition-all duration-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredResults.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No results found</div>
        ) : (
          filteredResults.map((result) => {
            const percentage = parseFloat(calculatePercentage(result.obtained_marks, result.total_marks));
            return (
              <div key={result.id} className="card">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{result.subject}</h3>
                    <p className="text-sm text-gray-500 mt-1">{result.exam_type}</p>
                  </div>
                  <Award className={`${getGradeColor(percentage)}`} size={24} />
                </div>
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Marks</span>
                    <span className="text-2xl font-bold text-gray-900">
                      {result.obtained_marks} / {result.total_marks}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        percentage >= 90
                          ? 'bg-green-500'
                          : percentage >= 80
                          ? 'bg-blue-500'
                          : percentage >= 70
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className={`font-semibold ${getGradeColor(percentage)}`}>
                    {percentage}%
                  </span>
                  <span className="text-gray-500">{result.remarks}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default StudentResults;

