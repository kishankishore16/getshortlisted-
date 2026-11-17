import React from 'react';
import { Award, CheckCircle, Lightbulb, FileText, ArrowRight } from 'lucide-react';
import { getScoreColor, getScoreGrade } from '@/lib/utils';

interface ResumeScoreCardProps {
  score: number;
  breakdown?: any;
  tips?: string[];
  onReScore?: () => void;
  isLoading?: boolean;
}

export const ResumeScoreCard: React.FC<ResumeScoreCardProps> = ({
  score,
  breakdown,
  tips = [],
  onReScore,
  isLoading = false,
}) => {
  const grade = getScoreGrade(score);
  const colorClass = getScoreColor(score);

  const comp = breakdown?.completeness || breakdown?.content || 80;
  const impact = breakdown?.impact_language || breakdown?.impact || 75;
  const kw = breakdown?.keyword_richness || breakdown?.keywords || 70;
  const struct = breakdown?.structure || breakdown?.formatting || 85;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Overall Health</span>
          <h3 className="text-lg font-bold text-slate-900">Resume Quality Score</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-extrabold px-3 py-1 rounded-full ${colorClass}`}>
            {Math.round(score)} / 100 • Grade {grade}
          </span>
          {onReScore && (
            <button
              onClick={onReScore}
              disabled={isLoading}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition text-slate-600 disabled:opacity-50"
            >
              {isLoading ? 'Scoring...' : 'Recalculate'}
            </button>
          )}
        </div>
      </div>

      {/* Breakdown Bars */}
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Completeness</span>
            <span className="font-semibold text-slate-900">{Math.round(comp)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${comp}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Impact & Metrics</span>
            <span className="font-semibold text-slate-900">{Math.round(impact)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${impact}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Keyword Richness</span>
            <span className="font-semibold text-slate-900">{Math.round(kw)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${kw}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-slate-600 mb-1">
            <span>Structure & Flow</span>
            <span className="font-semibold text-slate-900">{Math.round(struct)}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-purple-500 rounded-full" style={{ width: `${struct}%` }} />
          </div>
        </div>
      </div>

      {/* Actionable Tips */}
      {tips.length > 0 && (
        <div className="pt-2 border-t border-slate-100">
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Lightbulb className="w-3.5 h-3.5 text-amber-500" /> Actionable Improvement Tips
          </h4>
          <ul className="space-y-2">
            {tips.map((tip, i) => (
              <li key={i} className="text-xs text-slate-600 flex items-start gap-2 bg-amber-50/60 p-2.5 rounded-lg border border-amber-100">
                <ArrowRight className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
