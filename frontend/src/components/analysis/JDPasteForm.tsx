import React, { useState } from 'react';
import { Search, Sparkles, Building, Briefcase } from 'lucide-react';

interface JDPasteFormProps {
  onSubmit: (jdText: string, sourceHint: string) => void;
  isLoading: boolean;
}

export const JDPasteForm: React.FC<JDPasteFormProps> = ({ onSubmit, isLoading }) => {
  const [jdText, setJdText] = useState('');
  const [sourceHint, setSourceHint] = useState('LinkedIn');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (jdText.trim().length < 50) return;
    onSubmit(jdText, sourceHint);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Job Source (Optional)
          </label>
          <div className="relative">
            <select
              value={sourceHint}
              onChange={(e) => setSourceHint(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 bg-white text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 shadow-sm transition"
            >
              <option value="LinkedIn">LinkedIn Job Post</option>
              <option value="Naukri">Naukri.com</option>
              <option value="Indeed">Indeed</option>
              <option value="Company Portal">Company Career Portal</option>
              <option value="Internshala">Internshala</option>
              <option value="Other">Other Job Board / Email</option>
            </select>
            <Building className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
          </div>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5 flex justify-between">
          <span>Paste Job Description</span>
          <span className="text-slate-400 font-normal">Min. 50 characters</span>
        </label>
        <textarea
          rows={10}
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste full job description from LinkedIn, Naukri, or career page here (title, requirements, tech stack, responsibilities)..."
          className="w-full p-4 rounded-xl border border-slate-300 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 shadow-sm font-mono transition"
          required
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || jdText.trim().length < 50}
        className="w-full py-3.5 px-6 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-indigo-200 transition-all flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Analyzing Match with AI...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Analyze Match & Get Fit Score
          </>
        )}
      </button>
    </form>
  );
};
