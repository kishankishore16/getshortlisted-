import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Building, Calendar, ArrowRight, Trash2 } from 'lucide-react';
import { getScoreColor, getScoreGrade, formatDate } from '@/lib/utils';

interface AnalysisCardProps {
  analysis: any;
  onDelete?: (id: string) => void;
}

export const AnalysisCard: React.FC<AnalysisCardProps> = ({ analysis, onDelete }) => {
  const navigate = useNavigate();
  const title = analysis.job_title || analysis.jd_title || (analysis.jd_parsed && analysis.jd_parsed.title) || 'Software Role';
  const company = analysis.company || analysis.jd_company || (analysis.jd_parsed && analysis.jd_parsed.company) || 'Target Company';
  const score = Math.round(analysis.fit_score || 0);
  const grade = getScoreGrade(score);
  const colorClass = getScoreColor(score);
  const dateStr = formatDate(analysis.created_at);
  const source = analysis.source_hint || analysis.jd_source_hint || 'Direct Paste';

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
          <Briefcase className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-bold text-slate-900 text-sm md:text-base">{title}</h4>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
              {source}
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500 mt-1">
            <span className="flex items-center gap-1"><Building className="w-3.5 h-3.5 text-slate-400" /> {company}</span>
            <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-slate-400" /> {dateStr}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 self-end sm:self-center">
        <div className={`px-3 py-1.5 rounded-xl font-extrabold text-sm ${colorClass}`}>
          {score}% <span className="text-xs font-semibold">({grade})</span>
        </div>

        <button
          onClick={() => navigate(`/analyze/${analysis.id}`)}
          className="px-3.5 py-1.5 rounded-lg text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition flex items-center gap-1.5 shadow-sm"
        >
          View Match <ArrowRight className="w-3.5 h-3.5" />
        </button>

        {onDelete && (
          <button
            onClick={() => onDelete(analysis.id)}
            className="p-1.5 text-slate-400 hover:text-rose-600 transition"
            title="Delete analysis"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
