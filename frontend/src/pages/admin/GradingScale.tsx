import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { ArrowLeft, Plus, Trash2, RotateCcw } from 'lucide-react';
import { getGradeScale, saveGradeScale, resetGradeScale } from '../../services/api';
import type { GradeBand } from '../../types';
import { Modal } from '../../components/Modal';
import { showError, showSuccess } from '../../utils/errorHandler';

// One row while editing: the percentage is text so the box can be empty while typing
interface BandRow {
  grade: string;
  min_percentage: string;
}

// The school's grading scale: which grade a student gets for each percentage.
// It starts with the common scale (A+ 80, A 70, B 60, C 50, D 40, E 33, F 0),
// and the admin can change it to the school's own. Report cards use it straight away.
const AdminGradingScale: React.FC = () => {
  const navigate = useNavigate();
  const [rows, setRows] = useState<BandRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [isResetOpen, setIsResetOpen] = useState(false);

  useEffect(() => {
    fetchScale();
  }, []);

  const showScale = (scale: GradeBand[]) => {
    const newRows: BandRow[] = [];
    for (const band of scale) {
      newRows.push({ grade: band.grade, min_percentage: String(band.min_percentage) });
    }
    setRows(newRows);
  };

  const fetchScale = async () => {
    try {
      const data = await getGradeScale();
      showScale(Array.isArray(data) ? data : []);
    } catch (error: any) {
      showError(error, 'Failed to load the grading scale');
    } finally {
      setLoading(false);
    }
  };

  const changeRow = (index: number, field: 'grade' | 'min_percentage', value: string) => {
    const newRows: BandRow[] = [];
    for (let i = 0; i < rows.length; i++) {
      if (i === index) {
        newRows.push({ ...rows[i], [field]: value });
      } else {
        newRows.push(rows[i]);
      }
    }
    setRows(newRows);
  };

  const addRow = () => {
    setRows([...rows, { grade: '', min_percentage: '' }]);
  };

  const removeRow = (index: number) => {
    const newRows: BandRow[] = [];
    for (let i = 0; i < rows.length; i++) {
      if (i !== index) {
        newRows.push(rows[i]);
      }
    }
    setRows(newRows);
  };

  const handleSave = async () => {
    // Every row needs a grade and a percentage from 0 to 100
    const bands: { grade: string; min_percentage: number }[] = [];
    for (const row of rows) {
      if (row.grade.trim() === '' || row.min_percentage === '') {
        toast.error('Every row needs a grade and a starting percentage');
        return;
      }
      bands.push({ grade: row.grade.trim(), min_percentage: Number(row.min_percentage) });
    }

    try {
      const data = await saveGradeScale(bands);
      showSuccess(data.message || 'Grading scale saved');
      showScale(data.scale);
    } catch (error: any) {
      showError(error, 'Failed to save the grading scale');
    }
  };

  const handleReset = async () => {
    try {
      const data = await resetGradeScale();
      showSuccess(data.message || 'Grading scale reset');
      showScale(data.scale);
      setIsResetOpen(false);
    } catch (error: any) {
      showError(error, 'Failed to reset the grading scale');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <button onClick={() => navigate('/admin/exams')} className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1 mb-2">
          <ArrowLeft size={16} /> Exams
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Grading Scale</h1>
        <p className="text-gray-600 mt-2">
          The grade a student gets for each percentage. A student gets the highest grade whose starting percentage they reach.
          Report cards and result sheets use this scale.
        </p>
      </div>

      <div className="card space-y-4">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Grade</th>
                <th>From (%)</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  <td>
                    <input type="text" maxLength={5} value={row.grade} onChange={(e) => changeRow(index, 'grade', e.target.value)} className="input py-1 max-w-[7rem]" placeholder="e.g. A+" />
                  </td>
                  <td>
                    <input type="number" min={0} max={100} step={0.5} value={row.min_percentage} onChange={(e) => changeRow(index, 'min_percentage', e.target.value)} className="input py-1 max-w-[7rem]" />
                  </td>
                  <td>
                    <button onClick={() => removeRow(index)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Remove this grade">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-sm text-gray-500">The lowest grade must start at 0%, so every student gets a grade (for example F from 0%).</p>

        <div className="flex flex-wrap justify-between gap-2">
          <div className="flex gap-2">
            <button onClick={addRow} className="btn btn-secondary flex items-center gap-1"><Plus size={16} /> Add Grade</button>
            <button onClick={() => setIsResetOpen(true)} className="btn btn-secondary flex items-center gap-1"><RotateCcw size={16} /> Reset to Default</button>
          </div>
          <button onClick={handleSave} className="btn btn-primary">Save Scale</button>
        </div>
      </div>

      <Modal isOpen={isResetOpen} onClose={() => setIsResetOpen(false)} title="Reset the grading scale">
        <p className="text-sm text-gray-700">Go back to the default scale: A+ from 80%, A 70%, B 60%, C 50%, D 40%, E 33% and F below 33%?</p>
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={() => setIsResetOpen(false)} className="btn btn-secondary">Cancel</button>
          <button onClick={handleReset} className="btn btn-primary">Reset</button>
        </div>
      </Modal>
    </div>
  );
};

export default AdminGradingScale;
