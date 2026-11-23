import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ---- Types ----

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface Resume {
  id: string;
  filename: string;
  uploaded_at: string;
  parsed_data: ParsedResume | null;
  score: ResumeScore | null;
}

export interface ParsedResume {
  personal_info: {
    name: string;
    email: string;
    phone: string;
    location: string;
    linkedin: string;
    github: string;
    portfolio: string;
  };
  summary: string;
  skills: SkillCategory[];
  experience: Experience[];
  projects: Project[];
  education: Education[];
  certifications: Certification[];
}

export interface SkillCategory {
  category: string;
  skills: string[];
}

export interface Experience {
  title: string;
  company: string;
  location: string;
  start_date: string;
  end_date: string;
  description: string;
  highlights: string[];
}

export interface Project {
  name: string;
  description: string;
  tech_stack: string[];
  url: string;
  highlights: string[];
}

export interface Education {
  degree: string;
  institution: string;
  location: string;
  start_date: string;
  end_date: string;
  gpa: string;
}

export interface Certification {
  name: string;
  issuer: string;
  date: string;
  url: string;
}

export interface ResumeScore {
  overall_score: number;
  breakdown: {
    content: number;
    formatting: number;
    impact: number;
    keywords: number;
    completeness: number;
  };
  tips: string[];
  grade: string;
}

export interface Analysis {
  id: string;
  resume_id: string;
  created_at: string;
  job_title: string;
  company: string;
  source_hint: string;
  fit_score: number;
  score_breakdown: {
    semantic_similarity: number;
    skill_match: number;
    experience_relevance: number;
    education_fit: number;
  };
  why_you_fit: string;
  matched_skills: string[];
  missing_skills: MissingSkill[];
  keywords_present: string[];
  keywords_missing: KeywordMissing[];
  experience_level: string;
  jd_text: string;
}

export interface MissingSkill {
  skill: string;
  priority: 'required' | 'preferred' | 'nice-to-have';
  reason: string;
  learning_time: string;
  resources: { title: string; url: string }[];
}

export interface KeywordMissing {
  keyword: string;
  suggested_placement: string;
}

export interface EnhanceRequest {
  sections: string[];
}

export interface EnhancedSection {
  section: string;
  original: string;
  enhanced: string;
  changes: string[];
}

export interface EnhanceResult {
  id: string;
  analysis_id: string;
  sections: EnhancedSection[];
  ats_tips: string[];
  keywords_added: string[];
}

export const pingServer = () => api.get('/health').catch(() => {});

// ---- API Functions ----

export const authApi = {
  register: (data: RegisterData) =>
    api.post<AuthResponse>('/auth/register', data),

  login: (data: LoginData) =>
    api.post<AuthResponse>('/auth/login', data),

  getMe: () =>
    api.get<User>('/auth/me'),
};

export const resumeApi = {
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Resume>('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getResumes: () =>
    api.get<Resume[]>('/resumes'),

  getResume: (id: string) =>
    api.get<Resume>(`/resumes/${id}`),

  deleteResume: (id: string) =>
    api.delete(`/resumes/${id}`),

  scoreResume: (id: string) =>
    api.post<ResumeScore>(`/resumes/${id}/score`),
};

export const analyzeApi = {
  analyzeJob: (resumeId: string, jdText: string, sourceHint?: string) =>
    api.post<Analysis>('/analyze', { resume_id: resumeId, jd_text: jdText, source_hint: sourceHint }),

  getHistory: () =>
    api.get<Analysis[]>('/analyze/history'),

  getAnalysis: (id: string) =>
    api.get<Analysis>(`/analyze/${id}`),

  deleteAnalysis: (id: string) =>
    api.delete(`/analyze/${id}`),
};

export const enhanceApi = {
  enhanceResume: (analysisId: string, sections: string[]) =>
    api.post<EnhanceResult>(`/enhance/${analysisId}`, { sections }),
};

export default api;
