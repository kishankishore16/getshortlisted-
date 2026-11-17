import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { ResumeEnhanceView } from '@/components/resume/ResumeEnhanceView';
import { enhanceApi, analyzeApi } from '@/services/api';
import toast from 'react-hot-toast';
import {
  Sparkles,
  ArrowLeft,
  CheckSquare,
  Square,
  ShieldCheck,
  Tag,
  Copy,
  CheckCircle2,
} from 'lucide-react';

export const EnhanceResume: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();

  const [sections, setSections] = useState<string[]>(['summary', 'experience', 'skills', 'projects']);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [enhanceResult, setEnhanceResult] = useState<any>(null);

  useEffect(() => {
    if (!analysisId) return;
    const fetchAnalysis = async () => {
      try {
        const res = await analyzeApi.getAnalysis(analysisId);
        setAnalysis(res.data);
        if (res.data.enhancement_suggestions) {
          setEnhanceResult(res.data.enhancement_suggestions);
        }
      } catch (err) {
        toast.error('Failed to load analysis for enhancement.');
      }
    };
    fetchAnalysis();
  }, [analysisId]);

  const toggleSection = (s: string) => {
    if (sections.includes(s)) {
      setSections(sections.filter((x) => x !== s));
    } else {
      setSections([...sections, s]);
    }
  };

  const handleEnhance = async () => {
    if (!analysisId || sections.length === 0) {
      toast.error('Please select at least one section to enhance.');
      return;
    }

    setLoading(true);
    try {
      const res = await enhanceApi.enhanceResume(analysisId, sections);
      setEnhanceResult(res.data);
      toast.success('Resume rewritten and optimized!');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to enhance resume.');
    } finally {
      setLoading(false);
    }
  };

  const jobTitle = analysis?.jd_parsed?.title || analysis?.job_title || 'Target Job';
  const company = analysis?.jd_parsed?.company || analysis?.company || 'Company';

  return (
    <PageWrapper>
      <div className="space-y-8 pb-16">
        {/* Navigation & Header */}
        <div>
          <button
            onClick={() => navigate(analysisId ? `/analyze/${analysisId}` : '/dashboard')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition mb-3"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Match Breakdown
          </button>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-800 border border-slate-200 mb-1">
                Targeted Resume Customizer
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-950 tracking-tight">
                Role Revisions for {jobTitle}
              </h1>
              <p className="text-xs text-slate-600 mt-1">
                Calibrated for {company} using active voice, quantified outcomes, and relevant technical terminology
              </p>
            </div>
          </div>
        </div>

        {/* Section Selectors */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-sm">Select Sections to Optimize</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { id: 'summary', label: 'Summary / Objective' },
              { id: 'experience', label: 'Experience Bullets' },
              { id: 'skills', label: 'Skills Layout' },
              { id: 'projects', label: 'Project Descriptions' },
            ].map((sec) => {
              const selected = sections.includes(sec.id);
              return (
                <button
                  key={sec.id}
                  onClick={() => toggleSection(sec.id)}
                  type="button"
                  className={`p-3 rounded-xl border text-xs font-semibold text-left transition flex items-center justify-between ${
                    selected
                      ? 'border-indigo-600 bg-indigo-50/60 text-indigo-900'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span>{sec.label}</span>
                  {selected ? (
                    <CheckSquare className="w-4 h-4 text-indigo-600 shrink-0" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-300 shrink-0" />
                  )}
                </button>
              );
            })}
          </div>

          <button
            onClick={handleEnhance}
            disabled={loading || sections.length === 0}
            className="w-full py-3 rounded-lg font-semibold text-white bg-slate-950 hover:bg-slate-850 disabled:opacity-50 transition shadow-2xs text-xs flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Regenerating section revisions...
              </>
            ) : (
              <>
                <FileText className="w-3.5 h-3.5" />
                {enhanceResult ? 'Update Tailored Sections' : 'Generate Targeted Sections'}
              </>
            )}
          </button>
        </div>

        {/* Enhanced Sections Display */}
        {enhanceResult && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-900">Before & After Comparisons</h2>
              <span className="text-xs text-slate-500 font-medium">Click 'Copy Enhanced' to paste into your resume</span>
            </div>

            <div className="space-y-6">
              {(enhanceResult.sections || []).map((sec: any, idx: number) => (
                <ResumeEnhanceView
                  key={idx}
                  section={sec.section}
                  original={sec.original}
                  enhanced={sec.enhanced}
                  changes={sec.changes || sec.changes_made}
                />
              ))}
            </div>

            {/* ATS Tips & Keywords injected */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
              {/* ATS Tips */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-600" /> ATS Compatibility Guidelines
                </h4>
                <ul className="space-y-2 text-xs text-slate-600">
                  {(enhanceResult.ats_tips || []).map((tip: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Keywords Injected */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <Tag className="w-4 h-4 text-purple-600" /> High-Value Keywords Injected
                </h4>
                <p className="text-xs text-slate-500">
                  These keywords were woven into your enhanced resume bullets to maximize recruiter searchability:
                </p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(enhanceResult.keywords_added || []).map((kw: string, i: number) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  );
};
