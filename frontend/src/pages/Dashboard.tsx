import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Search,
  Sparkles,
  TrendingUp,
  Award,
  ArrowRight,
  PlusCircle,
  Building,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useResumeStore } from '@/store/resumeStore';
import { resumeApi, analyzeApi } from '@/services/api';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { AnalysisCard } from '@/components/history/AnalysisCard';
import { getScoreGrade, getScoreColor } from '@/lib/utils';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { resumes, setResumes, activeResume, setActiveResume, analyses, setAnalyses } = useResumeStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [resumesRes, analysesRes] = await Promise.all([
          resumeApi.getResumes(),
          analyzeApi.getHistory(),
        ]);
        setResumes(resumesRes.data);
        if (resumesRes.data.length > 0) {
          setActiveResume(resumesRes.data[0]);
        }
        setAnalyses(analysesRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalAnalyses = analyses.length;
  const avgFitScore =
    totalAnalyses > 0
      ? Math.round(analyses.reduce((acc, a) => acc + (a.fit_score || 0), 0) / totalAnalyses)
      : 0;
  const topMatch =
    totalAnalyses > 0
      ? Math.round(Math.max(...analyses.map((a) => a.fit_score || 0)))
      : 0;
  const resumeScore = Math.round(activeResume?.quality_score || (activeResume?.score as any)?.overall_score || 78);

  return (
    <PageWrapper>
      <div className="space-y-8">
        {/* Welcome Header */}
        <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 rounded-3xl p-8 text-white relative overflow-hidden shadow-lg shadow-indigo-950/20">
          <div className="relative z-10 space-y-3 max-w-2xl">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/30 text-indigo-200 border border-indigo-400/20">
              <Sparkles className="w-3.5 h-3.5" /> AI Job-Fit Coach
            </span>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Hey, {user?.full_name?.split(' ')[0] || 'Student'} 👋
            </h1>
            <p className="text-sm text-indigo-100 leading-relaxed">
              Match your resume against any job description from LinkedIn or Naukri to get an instant fit score, skill-gap analysis, and tailored rewrites.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <button
                onClick={() => navigate('/analyze')}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-white text-indigo-900 hover:bg-indigo-50 shadow-md transition flex items-center gap-2"
              >
                <Search className="w-4 h-4" /> Analyze a Job Description
              </button>
              <button
                onClick={() => navigate('/resume')}
                className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-indigo-700/60 hover:bg-indigo-700 text-white border border-indigo-500/30 transition flex items-center gap-2"
              >
                <FileText className="w-4 h-4" /> {activeResume ? 'View / Update Resume' : 'Upload Resume'}
              </button>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Target Roles Analyzed</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-slate-900">{totalAnalyses}</span>
              <span className="text-xs text-slate-400">JDs</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Average Fit Score</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-indigo-600">{avgFitScore}%</span>
              <span className="text-xs text-slate-400">({getScoreGrade(avgFitScore)})</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Highest Match Found</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-emerald-600">{topMatch}%</span>
              <span className="text-xs text-slate-400">top</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Resume Health Score</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-purple-600">
                {activeResume ? `${resumeScore}%` : 'N/A'}
              </span>
              <span className="text-xs text-slate-400">{activeResume ? getScoreGrade(resumeScore) : 'No file'}</span>
            </div>
          </div>
        </div>

        {/* Quick Active Resume Banner if none uploaded */}
        {!activeResume && !loading && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center shrink-0">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-amber-900 text-sm">Upload your resume to get started</h3>
                <p className="text-xs text-amber-700">
                  We need your resume PDF to match against job postings and generate tailored rewrites.
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/resume')}
              className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 transition shrink-0"
            >
              Upload Resume PDF
            </button>
          </div>
        )}

        {/* Recent Analyses List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Recent Job Matches</h2>
              <p className="text-xs text-slate-500">Your latest pasted job descriptions and fit ratings</p>
            </div>
            {totalAnalyses > 0 && (
              <button
                onClick={() => navigate('/history')}
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition flex items-center gap-1"
              >
                View all ({totalAnalyses}) <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {loading ? (
            <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-400 text-sm">
              Loading your dashboard data...
            </div>
          ) : analyses.length > 0 ? (
            <div className="space-y-3">
              {analyses.slice(0, 4).map((a) => (
                <AnalysisCard key={a.id} analysis={a} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
                <Search className="w-7 h-7" />
              </div>
              <div className="space-y-1">
                <h3 className="font-bold text-slate-900 text-base">No Job Analyses Yet</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Find a job posting on LinkedIn or Naukri, copy the text, and paste it to see your match score.
                </p>
              </div>
              <button
                onClick={() => navigate('/analyze')}
                className="px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200 transition"
              >
                Analyze First Job Description
              </button>
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  );
};
