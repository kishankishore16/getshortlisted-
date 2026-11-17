import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Rocket,
  Brain,
  Target,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Layers,
  Zap,
} from 'lucide-react';

export const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-900 text-white selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
              <Rocket className="w-5 h-5" />
            </div>
            <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              GetShortlisted
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white transition"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-4 py-2 text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl shadow-md shadow-indigo-600/30 transition"
            >
              Get Started Free
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(79,70,229,0.25),rgba(255,255,255,0))]" />

        <div className="max-w-4xl mx-auto text-center relative z-10 space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" /> Stop Applying Blindly. Start Getting Shortlisted.
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.15]">
            AI Resume Coach & <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-emerald-400 bg-clip-text text-transparent">
              Job-Fit Match Engine
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Upload your resume. Paste any job description from LinkedIn, Naukri, or career portals.
            Get an instant fit score, personalized skill-gap roadmap, and tailored resume rewrite in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-xl shadow-indigo-600/30 transition flex items-center justify-center gap-2 group text-sm"
            >
              Start Free Analysis
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition text-sm"
            >
              Existing Account
            </button>
          </div>

          {/* Trust badges */}
          <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500">
            <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-emerald-400" /> 100% Free for Students</span>
            <span className="flex items-center gap-1.5"><Zap className="w-4 h-4 text-indigo-400" /> Powered by Gemini 2.0 Flash</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-purple-400" /> ATS Compatibility Scored</span>
          </div>
        </div>
      </section>

      {/* 3 Step Workflow */}
      <section className="py-20 px-6 border-t border-slate-800 bg-slate-950/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-2 mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">How It Works</span>
            <h2 className="text-3xl font-extrabold text-white">Land More Tech Interviews in 3 Simple Steps</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 hover:border-slate-700 transition">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center font-extrabold text-lg">
                1
              </div>
              <h3 className="text-lg font-bold text-white">Upload Your Resume</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                PyMuPDF + Gemini extracts your skills, projects, degrees, and bullets into clean structured data with zero data loss.
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 hover:border-slate-700 transition">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center font-extrabold text-lg">
                2
              </div>
              <h3 className="text-lg font-bold text-white">Paste Any Job Description</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Found a dream role on LinkedIn or Naukri? Just copy-paste the JD text. Our AI parses requirements and generates semantic embeddings.
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 hover:border-slate-700 transition">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center font-extrabold text-lg">
                3
              </div>
              <h3 className="text-lg font-bold text-white">Get Fit Score & Rewrite</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                See your 0-100 fit score, an actionable skill roadmap, and one-click AI rewrites that optimize bullets with metrics and action verbs.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase */}
      <section className="py-20 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto space-y-16">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="space-y-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white">Beyond Keyword Matching: Semantic AI Vectors</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Traditional ATS checkers reject resumes over minor terminology differences. GetShortlisted uses sentence transformer embeddings to understand technical equivalence — recognizing that "Postgres" matches "PostgreSQL" and "K8s" matches "Kubernetes orchestration".
              </p>
            </div>
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-6 text-xs font-mono space-y-2 text-slate-300">
              <div className="text-indigo-400 font-bold">// Hybrid Scoring Formula</div>
              <div className="pl-2 border-l border-indigo-500/40">
                FitScore = (SemanticSimilarity * 0.40) +<br />
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(SkillMatch * 0.35) +<br />
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(ExperienceAlignment * 0.15) +<br />
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(EducationFit * 0.10)
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-6 space-y-3 order-2 md:order-1 text-xs">
              <div className="flex items-center gap-2 text-rose-400 font-bold">
                <Target className="w-4 h-4" /> Missing Skill: Redis Caching (Required)
              </div>
              <p className="text-slate-300">
                "Needed for handling low-latency session storage and distributed cache invalidation."
              </p>
              <div className="p-3 bg-slate-900 rounded-xl border border-slate-700 space-y-1">
                <span className="text-slate-400 block text-[11px] uppercase tracking-wider font-semibold">Fast Track (~3 days):</span>
                <span className="text-indigo-400">roadmap.sh/redis • freeCodeCamp Redis in 60 Mins</span>
              </div>
            </div>
            <div className="space-y-4 order-1 md:order-2">
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center">
                <Target className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white">Personalized Skill-Gap Roadmap</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Never wonder why you were ghosted again. GetShortlisted identifies exact technical gaps, estimates time to learn, and links free high-quality tutorials to bridge each gap.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <footer className="border-t border-slate-800 py-12 px-6 bg-slate-950 text-center space-y-6">
        <h3 className="text-2xl font-extrabold text-white">Ready to boost your interview callbacks?</h3>
        <button
          onClick={() => navigate('/register')}
          className="px-8 py-3.5 rounded-xl font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-xl shadow-indigo-600/30 transition inline-flex items-center gap-2 text-sm"
        >
          Build Your Free Profile Now <ArrowRight className="w-4 h-4" />
        </button>
        <p className="text-xs text-slate-600">
          © {new Date().getFullYear()} GetShortlisted. Built for students who deserve to get hired.
        </p>
      </footer>
    </div>
  );
};
