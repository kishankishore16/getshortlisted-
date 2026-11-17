import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { FitScoreCard } from '@/components/analysis/FitScoreCard';
import { WhyYouFit } from '@/components/analysis/WhyYouFit';
import { SkillGapList } from '@/components/analysis/SkillGapList';
import { SkillRadarChart } from '@/components/analysis/SkillRadarChart';
import { KeywordAnalysis } from '@/components/analysis/KeywordAnalysis';
import { analyzeApi } from '@/services/api';
import toast from 'react-hot-toast';
import {
  Sparkles,
  ArrowRight,
  Briefcase,
  Building,
  CheckCircle2,
  AlertCircle,
  FileText,
  Share2,
} from 'lucide-react';

export const AnalysisResult: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const res = await analyzeApi.getAnalysis(id);
        setAnalysis(res.data);
      } catch (err: any) {
        toast.error('Failed to load analysis result.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [id]);

  if (loading) {
    return (
      <PageWrapper>
        <div className="py-24 text-center space-y-3">
          <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-700">Loading your comprehensive match report...</p>
        </div>
      </PageWrapper>
    );
  }

  if (!analysis) {
    return (
      <PageWrapper>
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
          <h2 className="text-xl font-bold text-slate-900">Analysis Not Found</h2>
          <p className="text-xs text-slate-500">The requested job analysis does not exist or was deleted.</p>
          <button
            onClick={() => navigate('/analyze')}
            className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600"
          >
            Start New Analysis
          </button>
        </div>
      </PageWrapper>
    );
  }

  const jdParsed = analysis.jd_parsed || {};
  const jobTitle = jdParsed.title || analysis.job_title || 'Software Role';
  const company = jdParsed.company || analysis.company || 'Target Company';
  const expLevel = jdParsed.experience_level || analysis.experience_level || '0-2 years';

  const matchedSkills = analysis.matched_skills || [];
  const missingSkills = analysis.missing_skills || [];
  const kwAnalysis = analysis.keyword_analysis || {};
  const kwPresent = kwAnalysis.keywords_in_both || analysis.keywords_present || [];
  const kwMissing = kwAnalysis.keywords_to_add || kwAnalysis.keywords_missing_from_resume || analysis.keywords_missing || [];

  return (
    <PageWrapper>
      <div className="space-y-8 pb-12">
        {/* Top Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 mb-1">
              <span>Analysis ID: {analysis.id.slice(0, 8)}</span>
              <span>•</span>
              <span>Target: {company}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {jobTitle}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(`/enhance/${analysis.id}`)}
              className="px-5 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-md shadow-indigo-300 transition flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              Tailor Resume for This Job
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* 1. Hero FitScoreCard */}
        <FitScoreCard
          score={analysis.fit_score}
          breakdown={analysis.score_breakdown}
          jobTitle={jobTitle}
          company={company}
        />

        {/* 2. Why You Fit Highlight */}
        <WhyYouFit
          explanation={analysis.fit_explanation || analysis.why_you_fit}
          matchedCount={matchedSkills.length}
        />

        {/* 3. Skill Radar & Matched Skills Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <SkillRadarChart scoreBreakdown={analysis.score_breakdown} />
          </div>

          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Matched Skills & Strengths
              </h4>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700">
                {matchedSkills.length} matches
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Technologies and competencies from your resume that fulfill role criteria:
            </p>
            <div className="flex flex-wrap gap-2 pt-1">
              {matchedSkills.length > 0 ? (
                matchedSkills.map((m: any, idx: number) => {
                  const skillName = typeof m === 'string' ? m : m.resume_match || m.jd_skill || 'Skill';
                  return (
                    <span
                      key={idx}
                      className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      {skillName}
                    </span>
                  );
                })
              ) : (
                <span className="text-xs text-slate-400 italic">No direct skill matches detected.</span>
              )}
            </div>
          </div>
        </div>

        {/* 4. Actionable Skill Gaps Roadmap */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Missing Skills & Learning Roadmap</h3>
              <p className="text-xs text-slate-500">
                Targeted skills you should study or highlight to improve callback rate
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
              {missingSkills.length} gaps identified
            </span>
          </div>

          <SkillGapList missingSkills={missingSkills} />
        </div>

        {/* 5. ATS Keyword Analysis */}
        <div className="space-y-3">
          <h3 className="font-bold text-slate-900 text-base">Applicant Tracking System (ATS) Keyword Analysis</h3>
          <KeywordAnalysis keywordsPresent={kwPresent} keywordsMissing={kwMissing} />
        </div>

        {/* Bottom CTA to Enhance */}
        <div className="bg-gradient-to-r from-indigo-900 to-slate-900 rounded-3xl p-8 text-white flex flex-col sm:flex-row items-center justify-between gap-6 shadow-lg shadow-indigo-950/20">
          <div className="space-y-1 text-center sm:text-left">
            <h3 className="text-xl font-extrabold">Ready to turn this {Math.round(analysis.fit_score)}% match into an interview?</h3>
            <p className="text-xs text-indigo-200">
              Let the AI rewrite your professional summary, bullets, and skills specifically for {company}.
            </p>
          </div>
          <button
            onClick={() => navigate(`/enhance/${analysis.id}`)}
            className="px-6 py-3 rounded-xl font-bold text-xs bg-indigo-500 hover:bg-indigo-400 text-white shadow-md transition flex items-center gap-2 shrink-0"
          >
            <Sparkles className="w-4 h-4" /> Rewrite My Resume With AI
          </button>
        </div>
      </div>
    </PageWrapper>
  );
};
