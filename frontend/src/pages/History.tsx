import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { AnalysisCard } from '@/components/history/AnalysisCard';
import { ScoreTrendChart } from '@/components/history/ScoreTrendChart';
import { analyzeApi } from '@/services/api';
import toast from 'react-hot-toast';
import { Search, Sparkles, Filter, ArrowUpDown } from 'lucide-react';

export const History: React.FC = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'score'>('date');

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await analyzeApi.getHistory();
      setAnalyses(res.data);
    } catch (err) {
      toast.error('Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this analysis?')) return;
    try {
      await analyzeApi.deleteAnalysis(id);
      toast.success('Analysis deleted.');
      setAnalyses(analyses.filter((a) => a.id !== id));
    } catch (err) {
      toast.error('Failed to delete analysis.');
    }
  };

  // Filter & Sort
  const filtered = analyses.filter((a) => {
    const title = (a.job_title || a.jd_title || '').toLowerCase();
    const company = (a.company || a.jd_company || '').toLowerCase();
    const q = searchTerm.toLowerCase();
    return title.includes(q) || company.includes(q);
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === 'score') {
      return (b.fit_score || 0) - (a.fit_score || 0);
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <PageWrapper>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Match History</h1>
          <p className="text-xs text-slate-500">
            Review past job description analyses, fit scores, and tailored resumes
          </p>
        </div>

        {/* Score Trend Chart if >= 2 entries */}
        {analyses.length >= 2 && <ScoreTrendChart analyses={analyses} />}

        {/* Search & Sort Filters */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
          <div className="relative w-full sm:w-80">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter by role or company..."
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          </div>

          <div className="flex items-center gap-2 self-end sm:self-center">
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <ArrowUpDown className="w-3.5 h-3.5" /> Sort:
            </span>
            <button
              onClick={() => setSortBy('date')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                sortBy === 'date'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Latest
            </button>
            <button
              onClick={() => setSortBy('score')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                sortBy === 'score'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Highest Fit
            </button>
          </div>
        </div>

        {/* Analyses List */}
        {loading ? (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 text-slate-400 text-sm">
            Loading analysis records...
          </div>
        ) : sorted.length > 0 ? (
          <div className="space-y-3">
            {sorted.map((item) => (
              <AnalysisCard key={item.id} analysis={item} onDelete={handleDelete} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-4">
            <h3 className="font-bold text-slate-900 text-base">No Matching Analyses</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              {searchTerm
                ? 'No job matches found matching your search term.'
                : 'You have not analyzed any job descriptions yet.'}
            </p>
            <button
              onClick={() => navigate('/analyze')}
              className="px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition"
            >
              Analyze a Job Posting
            </button>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};
