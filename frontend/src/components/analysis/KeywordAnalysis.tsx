import React from 'react';
import { Check, PlusCircle, Target } from 'lucide-react';

interface KeywordAnalysisProps {
  keywordsPresent?: string[];
  keywordsMissing?: any[];
}

export const KeywordAnalysis: React.FC<KeywordAnalysisProps> = ({
  keywordsPresent = [],
  keywordsMissing = [],
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Present Keywords */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-md bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <Check className="w-3.5 h-3.5" />
          </div>
          <h4 className="font-semibold text-slate-900 text-sm">Matching ATS Keywords ({keywordsPresent.length})</h4>
        </div>
        <p className="text-xs text-slate-500 mb-3">Found in both your resume and the job description:</p>
        <div className="flex flex-wrap gap-1.5">
          {keywordsPresent.length > 0 ? (
            keywordsPresent.map((kw, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200"
              >
                {kw}
              </span>
            ))
          ) : (
            <span className="text-xs text-slate-400 italic">No direct keyword overlap found</span>
          )}
        </div>
      </div>

      {/* Missing Keywords */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-6 h-6 rounded-md bg-rose-100 text-rose-600 flex items-center justify-center">
            <Target className="w-3.5 h-3.5" />
          </div>
          <h4 className="font-semibold text-slate-900 text-sm">Target Keywords to Add ({keywordsMissing.length})</h4>
        </div>
        <p className="text-xs text-slate-500 mb-3">Keywords ATS parsers look for that are absent in your resume:</p>
        <div className="space-y-2">
          {keywordsMissing.length > 0 ? (
            keywordsMissing.map((item: any, i: number) => {
              const kw = typeof item === 'string' ? item : item.keyword || item.name;
              const place = typeof item === 'object' ? item.suggested_placement : null;
              return (
                <div
                  key={i}
                  className="flex items-start justify-between gap-2 p-2 rounded-lg bg-rose-50/50 border border-rose-100 text-xs"
                >
                  <span className="font-semibold text-rose-900">{kw}</span>
                  {place && (
                    <span className="text-[11px] text-slate-500 italic text-right">
                      Suggest: {place}
                    </span>
                  )}
                </div>
              );
            })
          ) : (
            <span className="text-xs text-slate-400 italic">No critical missing keywords</span>
          )}
        </div>
      </div>
    </div>
  );
};
