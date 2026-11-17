import React from 'react';
import { Mail, Phone, MapPin, Linkedin, Github, Globe, GraduationCap, Briefcase, Code, Award } from 'lucide-react';

interface ParsedResumeViewProps {
  parsedData: any;
}

export const ParsedResumeView: React.FC<ParsedResumeViewProps> = ({ parsedData }) => {
  if (!parsedData) {
    return (
      <div className="p-8 text-center bg-slate-50 border border-slate-200 rounded-2xl text-slate-500 text-sm">
        No parsed resume data available. Upload your resume to extract details.
      </div>
    );
  }

  const personal = parsedData.personal_info || {
    name: parsedData.name,
    email: parsedData.email,
    phone: parsedData.phone,
    location: parsedData.location,
    linkedin: parsedData.linkedin,
    github: parsedData.github,
    portfolio: parsedData.portfolio,
  };

  const skillsObj = parsedData.skills || {};
  const experiences = parsedData.experience || [];
  const projects = parsedData.projects || [];
  const education = parsedData.education || [];
  const certifications = parsedData.certifications || [];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-8">
      {/* Header Info */}
      <div className="border-b border-slate-100 pb-6">
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {personal.name || 'Candidate Name'}
        </h2>
        <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-600">
          {personal.email && (
            <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-slate-400" /> {personal.email}</span>
          )}
          {personal.phone && (
            <span className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5 text-slate-400" /> {personal.phone}</span>
          )}
          {personal.location && (
            <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-slate-400" /> {personal.location}</span>
          )}
          {personal.github && (
            <a href={personal.github} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-indigo-600 hover:underline">
              <Github className="w-3.5 h-3.5" /> GitHub
            </a>
          )}
          {personal.linkedin && (
            <a href={personal.linkedin} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-indigo-600 hover:underline">
              <Linkedin className="w-3.5 h-3.5" /> LinkedIn
            </a>
          )}
        </div>
      </div>

      {/* Summary */}
      {parsedData.summary && (
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Professional Summary</h3>
          <p className="text-slate-700 text-sm leading-relaxed">{parsedData.summary}</p>
        </div>
      )}

      {/* Skills */}
      <div>
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
          <Code className="w-4 h-4 text-indigo-500" /> Technical Skills
        </h3>
        {Array.isArray(skillsObj) ? (
          <div className="space-y-3">
            {skillsObj.map((cat: any, i: number) => (
              <div key={i}>
                <span className="text-xs font-semibold text-slate-700 block mb-1.5">{cat.category}:</span>
                <div className="flex flex-wrap gap-1.5">
                  {(cat.skills || []).map((s: string, j: number) => (
                    <span key={j} className="px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {Object.entries(skillsObj).map(([cat, list]: [string, any], i) => (
              <div key={i}>
                <span className="text-xs font-semibold text-slate-700 block mb-1.5">{cat}:</span>
                <div className="flex flex-wrap gap-1.5">
                  {Array.isArray(list) &&
                    list.map((s: string, j: number) => (
                      <span key={j} className="px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                        {s}
                      </span>
                    ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Experience */}
      {experiences.length > 0 && (
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-indigo-500" /> Work Experience
          </h3>
          <div className="space-y-4">
            {experiences.map((exp: any, i: number) => (
              <div key={i} className="border-l-2 border-indigo-200 pl-4 space-y-1">
                <div className="flex justify-between items-baseline flex-wrap gap-1">
                  <h4 className="font-bold text-slate-900 text-sm">{exp.title || 'Role'}</h4>
                  <span className="text-xs text-slate-500">{exp.start_date} - {exp.end_date || 'Present'}</span>
                </div>
                <p className="text-xs font-medium text-slate-600">{exp.company} {exp.location ? `• ${exp.location}` : ''}</p>
                {exp.description && <p className="text-xs text-slate-600 mt-1">{exp.description}</p>}
                {(exp.bullets || exp.highlights || []).length > 0 && (
                  <ul className="list-disc list-inside text-xs text-slate-600 mt-2 space-y-1">
                    {(exp.bullets || exp.highlights).map((b: string, j: number) => (
                      <li key={j} className="leading-relaxed">{b}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Projects */}
      {projects.length > 0 && (
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Award className="w-4 h-4 text-indigo-500" /> Projects
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((proj: any, i: number) => (
              <div key={i} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2">
                <h4 className="font-bold text-slate-900 text-sm">{proj.name || 'Project'}</h4>
                <p className="text-xs text-slate-600 leading-relaxed">{proj.description}</p>
                {(proj.technologies || proj.tech_stack || []).length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {(proj.technologies || proj.tech_stack).map((t: string, j: number) => (
                      <span key={j} className="text-[10px] font-semibold px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {education.length > 0 && (
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-indigo-500" /> Education
          </h3>
          <div className="space-y-3">
            {education.map((edu: any, i: number) => (
              <div key={i} className="flex justify-between items-start text-xs border-b border-slate-100 pb-2">
                <div>
                  <p className="font-bold text-slate-900">{edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}</p>
                  <p className="text-slate-600">{edu.institution}</p>
                </div>
                <div className="text-right">
                  <span className="text-slate-500">{edu.end_date || edu.year || '2026'}</span>
                  {edu.gpa && <p className="font-semibold text-indigo-600">GPA: {edu.gpa}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
