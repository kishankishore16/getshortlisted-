import React, { useState } from 'react';
import { AlertCircle, Clock, ExternalLink, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

export interface SkillGapItem {
  skill_name?: string;
  skill?: string;
  priority: string;
  reason: string;
  estimated_learning_time?: string;
  learning_time?: string;
  resources: any[];
}

interface SkillGapListProps {
  missingSkills: SkillGapItem[];
}

export const SkillGapList: React.FC<SkillGapListProps> = ({ missingSkills }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!missingSkills || missingSkills.length === 0) {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-emerald-800 text-sm">
        🎉 Impressive! You have no critical missing skills for this job description.
      </div>
    );
  }

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="space-y-3">
      {missingSkills.map((item, idx) => {
        const name = item.skill_name || item.skill || 'Skill';
        const time = item.estimated_learning_time || item.learning_time || '1-2 weeks';
        const isRequired = item.priority?.toLowerCase() === 'required';
        const isExpanded = expandedIndex === idx;

        return (
          <div
            key={idx}
            className="border border-slate-200 rounded-xl bg-white overflow-hidden transition-all shadow-sm"
          >
            <button
              onClick={() => toggleExpand(idx)}
              className="w-full text-left px-5 py-4 flex items-center justify-between gap-4 hover:bg-slate-50/70"
            >
              <div className="flex items-center gap-3 flex-wrap">
                <span className="font-semibold text-slate-900 text-sm">{name}</span>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                    isRequired
                      ? 'bg-rose-100 text-rose-700'
                      : 'bg-amber-100 text-amber-700'
                  }`}
                >
                  {isRequired ? 'Required' : 'Preferred'}
                </span>
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" /> ~{time}
                </span>
              </div>
              <div className="text-slate-400">
                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>

            {isExpanded && (
              <div className="px-5 pb-5 pt-1 border-t border-slate-100 bg-slate-50/40 text-sm">
                <div className="mb-3">
                  <span className="font-medium text-slate-700 block mb-1">Why this matters:</span>
                  <p className="text-slate-600 text-xs md:text-sm leading-relaxed">{item.reason}</p>
                </div>

                {item.resources && item.resources.length > 0 && (
                  <div>
                    <span className="font-medium text-slate-700 block mb-1.5 flex items-center gap-1.5 text-xs uppercase tracking-wider">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-500" /> Recommended Fast-Track Resources
                    </span>
                    <ul className="space-y-1.5">
                      {item.resources.map((res: any, rIdx: number) => {
                        const url = typeof res === 'string' ? res : res.url;
                        const title = typeof res === 'string' ? res : res.title || url;
                        return (
                          <li key={rIdx}>
                            <a
                              href={url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 hover:underline break-all"
                            >
                              <ExternalLink className="w-3 h-3 shrink-0" />
                              {title}
                            </a>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
