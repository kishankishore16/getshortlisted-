import { create } from 'zustand';
import type { Resume, Analysis } from '@/services/api';

interface ResumeState {
  resumes: Resume[];
  activeResume: Resume | null;
  analyses: Analysis[];
  setResumes: (resumes: Resume[]) => void;
  setActiveResume: (resume: Resume | null) => void;
  addResume: (resume: Resume) => void;
  removeResume: (id: string) => void;
  setAnalyses: (analyses: Analysis[]) => void;
  addAnalysis: (analysis: Analysis) => void;
  removeAnalysis: (id: string) => void;
}

export const useResumeStore = create<ResumeState>((set) => ({
  resumes: [],
  activeResume: null,
  analyses: [],

  setResumes: (resumes) => set({ resumes }),

  setActiveResume: (resume) => set({ activeResume: resume }),

  addResume: (resume) =>
    set((state) => ({
      resumes: [resume, ...state.resumes],
      activeResume: resume,
    })),

  removeResume: (id) =>
    set((state) => ({
      resumes: state.resumes.filter((r) => r.id !== id),
      activeResume: state.activeResume?.id === id ? null : state.activeResume,
    })),

  setAnalyses: (analyses) => set({ analyses }),

  addAnalysis: (analysis) =>
    set((state) => ({
      analyses: [analysis, ...state.analyses],
    })),

  removeAnalysis: (id) =>
    set((state) => ({
      analyses: state.analyses.filter((a) => a.id !== id),
    })),
}));
