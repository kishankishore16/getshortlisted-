import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { formatDate } from '@/lib/utils';

interface ScoreTrendChartProps {
  analyses: any[];
}

export const ScoreTrendChart: React.FC<ScoreTrendChartProps> = ({ analyses }) => {
  if (!analyses || analyses.length === 0) return null;

  // Reverse chronological to chronological
  const chartData = [...analyses]
    .reverse()
    .slice(-10)
    .map((a, idx) => ({
      name: a.job_title || a.jd_title || `Job ${idx + 1}`,
      score: Math.round(a.fit_score || 0),
      date: formatDate(a.created_at),
    }));

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="mb-4">
        <h3 className="font-bold text-slate-900 text-sm">Fit Score Improvement Over Time</h3>
        <p className="text-xs text-slate-500">Track how your targeted changes increase role alignment</p>
      </div>
      <div className="w-full h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                color: '#fff',
                borderRadius: '8px',
                fontSize: '12px',
                border: 'none',
              }}
              formatter={(value: any) => [`${value}%`, 'Fit Score']}
            />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#4f46e5"
              strokeWidth={3}
              dot={{ fill: '#4f46e5', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
