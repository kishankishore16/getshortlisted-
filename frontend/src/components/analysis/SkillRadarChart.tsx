import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface SkillRadarChartProps {
  scoreBreakdown?: {
    semantic_similarity: number;
    skill_match: number;
    experience_relevance?: number;
    experience_alignment?: number;
    education_fit: number;
  };
}

export const SkillRadarChart: React.FC<SkillRadarChartProps> = ({ scoreBreakdown }) => {
  const semantic = scoreBreakdown?.semantic_similarity ?? 75;
  const skills = scoreBreakdown?.skill_match ?? 70;
  const exp = scoreBreakdown?.experience_alignment ?? scoreBreakdown?.experience_relevance ?? 65;
  const edu = scoreBreakdown?.education_fit ?? 85;

  const data = [
    { subject: 'Skills Match', score: Math.round(skills), fullMark: 100 },
    { subject: 'Semantic Match', score: Math.round(semantic), fullMark: 100 },
    { subject: 'Experience Fit', score: Math.round(exp), fullMark: 100 },
    { subject: 'Education Fit', score: Math.round(edu), fullMark: 100 },
    { subject: 'Tech Depth', score: Math.round((skills + semantic) / 2), fullMark: 100 },
  ];

  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col items-center">
      <h4 className="font-semibold text-slate-900 text-sm mb-1 self-start">Fit Competency Radar</h4>
      <p className="text-xs text-slate-500 mb-2 self-start">Multidimensional alignment with job requirements</p>
      <div className="w-full h-56">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 11 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#cbd5e1" />
            <Radar
              name="Fit Score"
              dataKey="score"
              stroke="#4f46e5"
              fill="#4f46e5"
              fillOpacity={0.4}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                color: '#f8fafc',
                borderRadius: '8px',
                fontSize: '12px',
                border: 'none',
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
