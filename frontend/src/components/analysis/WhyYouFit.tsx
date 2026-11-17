import React from 'react';
import { CheckCircle2, Award } from 'lucide-react';

interface WhyYouFitProps {
  explanation: string;
  matchedCount?: number;
}

export const WhyYouFit: React.FC<WhyYouFitProps> = ({ explanation, matchedCount }) => {
  return (
    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-2xs">
      <div className="flex items-start gap-3.5">
        <div className="w-9 h-9 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0">
          <Award className="w-4 h-4" />
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-slate-950">Candidate Qualification Assessment</h3>
            {matchedCount !== undefined && matchedCount > 0 && (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-800 border border-slate-200">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" /> {matchedCount} Criteria Met
              </span>
            )}
          </div>
          <p className="text-slate-700 leading-relaxed text-xs sm:text-sm">
            {explanation || "Your technical background demonstrates solid alignment with the requirements."}
          </p>
        </div>
      </div>
    </div>
  );
};
