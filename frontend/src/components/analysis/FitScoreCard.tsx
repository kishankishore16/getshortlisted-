import React from 'react';
import { getScoreColor, getScoreGrade } from '@/lib/utils';
import { Award, TrendingUp, CheckCircle, Brain, BookOpen } from 'lucide-react';

interface ScoreBreakdownProps {
  semantic_similarity: number;
  skill_match: number;
  experience_relevance?: number;
  experience_alignment?: number;
  education_fit: number;
  overall?: number;
}

interface FitScoreCardProps {
  score: number;
  breakdown?: ScoreBreakdownProps | null;
  jobTitle?: string;
  company?: string;
}

export const FitScoreCard: React.FC<FitScoreCardProps> = ({
  score,
  breakdown,
  jobTitle,
  company,
}) => {
  const grade = getScoreGrade(score);
  const colorClass = getScoreColor(score);

  const expScore = breakdown?.experience_alignment ?? breakdown?.experience_relevance ?? 70;
  const semanticScore = breakdown?.semantic_similarity ?? score;
  const skillScore = breakdown?.skill_match ?? score;
  const eduScore = breakdown?.education_fit ?? 80;

  // SVG circle circumference
  const radius = 58;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
      <div className="flex flex-col lg:flex-row items-center gap-8">
        {/* Circular Gauge */}
        <div className="relative flex items-center justify-center">
          <svg className="w-36 h-36 transform -rotate-90">
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke="currentColor"
              strokeWidth="10"
              fill="transparent"
              className="text-slate-100"
            />
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke="currentColor"
              strokeWidth="10"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className={`transition-all duration-1000 ease-out ${
                score >= 80 ? 'text-emerald-500' : score >= 60 ? 'text-indigo-600' : 'text-amber-500'
              }`}
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {Math.round(score)}%
            </span>
            <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${colorClass}`}>
              Grade {grade}
            </span>
          </div>
        </div>

        {/* Title and breakdown */}
        <div className="flex-1 w-full">
          <div className="mb-4 text-center lg:text-left">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 mb-1">
              <Award className="w-3.5 h-3.5" /> AI Job-Fit Evaluation
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              {jobTitle || 'Target Role Analysis'}
            </h2>
            {company && <p className="text-sm text-slate-500">{company}</p>}
          </div>

          {/* Breakdown progress bars */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span className="flex items-center gap-1"><Brain className="w-3.5 h-3.5 text-indigo-500" /> Semantic Match (40%)</span>
                <span className="font-semibold text-slate-900">{Math.round(semanticScore)}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, semanticScore))}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span className="flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> Skill Overlap (35%)</span>
                <span className="font-semibold text-slate-900">{Math.round(skillScore)}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, skillScore))}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span className="flex items-center gap-1"><TrendingUp className="w-3.5 h-3.5 text-purple-500" /> Experience Fit (15%)</span>
                <span className="font-semibold text-slate-900">{Math.round(expScore)}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-500 rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, expScore))}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span className="flex items-center gap-1"><BookOpen className="w-3.5 h-3.5 text-blue-500" /> Education & Degree (10%)</span>
                <span className="font-semibold text-slate-900">{Math.round(eduScore)}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(5, eduScore))}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
