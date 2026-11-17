import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { JDPasteForm } from '@/components/analysis/JDPasteForm';
import { useResumeStore } from '@/store/resumeStore';
import { resumeApi, analyzeApi } from '@/services/api';
import toast from 'react-hot-toast';
import { Search, Sparkles, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';

export const AnalyzeJob: React.FC = () => {
  const navigate = useNavigate();
  const { activeResume, setActiveResume, setResumes, resumes } = useResumeStore();
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    const fetchResumes = async () => {
      try {
        const res = await resumeApi.getResumes();
        setResumes(res.data);
        if (res.data.length > 0 && !activeResume) {
          setActiveResume(res.data[0]);
        }
      } catch (err) {
        console.error('Failed to load resume:', err);
      } finally {
        setInitLoading(false);
      }
    };
    fetchResumes();
  }, []);

  const handleAnalyze = async (jdText: string, sourceHint: string) => {
    if (!activeResume) {
      toast.error('Please upload your resume first!');
      navigate('/resume');
      return;
    }

    setLoading(true);
    try {
      const res = await analyzeApi.analyzeJob(activeResume.id, jdText, sourceHint);
      toast.success('Job-fit analysis complete!');
      navigate(`/analyze/${res.data.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to analyze job description.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-800 border border-slate-200 mb-2">
            Role Compatibility Assessment
          </div>
          <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Job Specification Analysis</h1>
          <p className="text-xs text-slate-600">
            Paste job requirements from LinkedIn, Naukri, or career portals to benchmark qualification fit and identify missing technical competencies.
          </p>
        </div>

        {/* Warning if no active resume */}
        {!activeResume && !initLoading && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-amber-600 shrink-0" />
              <div>
                <h4 className="text-sm font-bold text-amber-900">No Resume Uploaded</h4>
                <p className="text-xs text-amber-700">You need an active resume on file to compute match scores.</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/resume')}
              className="px-4 py-2 text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 rounded-xl transition shrink-0"
            >
              Upload Resume
            </button>
          </div>
        )}

        {/* Active Resume Indicator */}
        {activeResume && (
          <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
              <span>
                Matching against: <strong className="text-slate-900">{activeResume.parsed_data?.name || 'Active Resume'}</strong>
              </span>
            </div>
            <button
              onClick={() => navigate('/resume')}
              className="text-indigo-600 font-semibold hover:underline"
            >
              Switch Resume
            </button>
          </div>
        )}

        {/* Paste Form Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm">
          <JDPasteForm onSubmit={handleAnalyze} isLoading={loading} />
        </div>

        {/* Tips Box */}
        <div className="bg-slate-50 rounded-2xl border border-slate-200 p-5 text-xs text-slate-600 space-y-2">
          <h4 className="font-bold text-slate-900 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
            💡 Best Results Tip
          </h4>
          <p>
            Copy the <strong>complete</strong> job posting including the About the Role, Requirements, Tech Stack, and Responsibilities. More context allows the LLM and vector embeddings to accurately calculate your semantic similarity and pinpoint genuine skill gaps.
          </p>
        </div>
      </div>
    </PageWrapper>
  );
};
