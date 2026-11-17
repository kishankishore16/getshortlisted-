import React from 'react';
import { Sparkles, ArrowRight, CheckCircle2, Copy } from 'lucide-react';
import toast from 'react-hot-toast';

interface EnhancedSectionProps {
  section: string;
  original: string;
  enhanced: string;
  changes?: string[];
  changes_made?: string[];
}

export const ResumeEnhanceView: React.FC<EnhancedSectionProps> = ({
  section,
  original,
  enhanced,
  changes = [],
  changes_made = [],
}) => {
  const allChanges = changes.length > 0 ? changes : changes_made;

  const handleCopy = () => {
    navigator.clipboard.writeText(enhanced);
    toast.success(`Copied enhanced ${section} to clipboard!`);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs uppercase">
            <Sparkles className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-slate-900 capitalize text-base">
            {section} Section
          </h3>
        </div>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-700 transition"
        >
          <Copy className="w-3.5 h-3.5" /> Copy Enhanced
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Original */}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
            Original Resume
          </span>
          <p className="text-xs text-slate-600 font-mono whitespace-pre-wrap leading-relaxed">
            {original || 'No prior content found.'}
          </p>
        </div>

        {/* Enhanced */}
        <div className="p-4 rounded-xl bg-indigo-50/40 border border-indigo-200 relative">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-indigo-700 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> AI Tailored & Optimized
            </span>
          </div>
          <p className="text-xs text-slate-800 font-mono whitespace-pre-wrap leading-relaxed font-medium">
            {enhanced}
          </p>
        </div>
      </div>

      {/* Changes list */}
      {allChanges.length > 0 && (
        <div className="pt-2">
          <span className="text-xs font-bold text-slate-700 block mb-2">Key Optimizations Applied:</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {allChanges.map((change, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-600">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                <span>{change}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
