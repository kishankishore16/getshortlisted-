import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Layers,
  Target,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  FileCheck2,
  LineChart,
  BookOpen,
} from 'lucide-react';

export const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white text-slate-900 selection:bg-slate-900 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-slate-950 flex items-center justify-center text-white font-black text-sm tracking-tighter">
              GS
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-bold text-base tracking-tight text-slate-950">
                GetShortlisted
              </span>
              <span className="text-[11px] font-medium text-slate-600 hidden sm:inline">
                Placement & Career Match Suite
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/login')}
              className="text-xs font-semibold text-slate-600 hover:text-slate-950 transition"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-4 py-2 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition shadow-sm"
            >
              Create Student Account
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-6 border-b border-slate-100 bg-slate-50/50">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-slate-200 bg-white text-slate-700 text-xs font-medium shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Technical Shortlisting & Resume Tailoring Engine
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-950 leading-tight">
            Know exactly how your resume scores against any job description.
          </h1>

          <p className="text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            A precise evaluation tool for engineering students. Paste role requirements from LinkedIn, Naukri, or career portals to benchmark your skills, identify technical gaps, and generate role-tailored revisions.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-6 py-3 rounded-lg font-semibold bg-slate-950 hover:bg-slate-800 text-white shadow-sm transition flex items-center justify-center gap-2 text-xs"
            >
              Start Free Evaluation
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto px-6 py-3 rounded-lg font-semibold bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 transition text-xs"
            >
              Sign In to Dashboard
            </button>
          </div>

          <div className="pt-6 flex flex-wrap items-center justify-center gap-8 text-xs text-slate-500 font-medium">
            <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-slate-700" /> Free for Undergraduates</span>
            <span className="flex items-center gap-1.5"><FileCheck2 className="w-4 h-4 text-slate-700" /> ATS Compatibility Scored</span>
            <span className="flex items-center gap-1.5"><LineChart className="w-4 h-4 text-slate-700" /> Statistical Vector Ranking</span>
          </div>
        </div>
      </section>

      {/* 3 Step Workflow */}
      <section className="py-16 px-6 max-w-6xl mx-auto">
        <div className="text-center space-y-1 mb-12">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">The Evaluation Workflow</span>
          <h2 className="text-2xl font-bold text-slate-950">How Candidates Benchmark Their Profile</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-3 shadow-2xs hover:border-slate-300 transition">
            <div className="w-9 h-9 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center font-bold text-sm">
              01
            </div>
            <h3 className="text-base font-bold text-slate-950">Parse Master Resume</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Extract technical skills, completed projects, work experience, and degree qualifications into a structured career profile.
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-3 shadow-2xs hover:border-slate-300 transition">
            <div className="w-9 h-9 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center font-bold text-sm">
              02
            </div>
            <h3 className="text-base font-bold text-slate-950">Benchmark Against JD</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Copy any job posting. The engine computes semantic overlap, required vs. preferred competency match, and education criteria.
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-3 shadow-2xs hover:border-slate-300 transition">
            <div className="w-9 h-9 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center font-bold text-sm">
              03
            </div>
            <h3 className="text-base font-bold text-slate-950">Tailor & Close Skill Gaps</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Review your 0–100 match rating, curated learning paths for missing requirements, and export role-tailored bullet points.
            </p>
          </div>
        </div>
      </section>

      {/* Feature Showcase */}
      <section className="py-16 px-6 border-t border-slate-200 bg-slate-50/40">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="space-y-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">Methodology</span>
              <h3 className="text-xl font-bold text-slate-950">Hybrid Weighted Scoring Algorithm</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Rather than primitive keyword counts, GetShortlisted evaluates multidimensional role readiness using dense semantic embeddings and normalized skill taxonomies.
              </p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 text-xs font-mono space-y-2 text-slate-700 shadow-2xs">
              <div className="text-slate-950 font-bold"># Evaluation Weights</div>
              <div className="pl-3 border-l-2 border-slate-300 space-y-1 text-[11px]">
                <div>• Semantic Context: 40%</div>
                <div>• Required Skills: 35%</div>
                <div>• Practical Experience: 15%</div>
                <div>• Degree & GPA Criteria: 10%</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-10 px-6 bg-white text-center space-y-4">
        <div className="flex items-center justify-center gap-2 text-sm font-bold text-slate-950">
          <Briefcase className="w-4 h-4 text-slate-700" /> GetShortlisted Platform
        </div>
        <p className="text-xs text-slate-500">
          Designed for university placement preparation and campus hiring benchmarks.
        </p>
      </footer>
    </div>
  );
};
