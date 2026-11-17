import React from 'react';
import { Sparkles, ThumbsUp } from 'lucide-react';

interface WhyYouFitProps {
  explanation: string;
  matchedCount?: number;
}

export const WhyYouFit: React.FC<WhyYouFitProps> = ({ explanation, matchedCount }) => {
  return (
    <div className="bg-gradient-to-br from-indigo-50/70 to-emerald-50/50 rounded-2xl p-6 border border-indigo-100 shadow-sm relative overflow-hidden">
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-indigo-200">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-base font-bold text-slate-900">Why You Fit This Role</h3>
            {matchedCount !== undefined && matchedCount > 0 && (
              <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                <ThumbsUp className="w-3 h-3" /> {matchedCount} skills matched
              </span>
            )}
          </div>
          <p className="text-slate-700 leading-relaxed text-sm md:text-base font-normal">
            {explanation || "Your background and capabilities demonstrate solid alignment with the requirements."}
          </p>
        </div>
      </div>
    </div>
  );
};
