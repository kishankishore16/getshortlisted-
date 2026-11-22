import React, { useEffect, useState } from 'react';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { ResumeUpload } from '@/components/resume/ResumeUpload';
import { ParsedResumeView } from '@/components/resume/ParsedResumeView';
import { ResumeScoreCard } from '@/components/resume/ResumeScoreCard';
import { useResumeStore } from '@/store/resumeStore';
import { resumeApi } from '@/services/api';
import toast from 'react-hot-toast';
import { UploadCloud, FileText, CheckCircle2 } from 'lucide-react';

export const ResumeManager: React.FC = () => {
  const { resumes, activeResume, setResumes, setActiveResume } = useResumeStore();
  const [isUploading, setIsUploading] = useState(false);
  const [isScoring, setIsScoring] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    const fetchResumes = async () => {
      try {
        const res = await resumeApi.getResumes();
        setResumes(res.data);
        if (res.data.length > 0 && !activeResume) {
          setActiveResume(res.data[0]);
        }
      } catch (err) {
        console.error('Failed to load resumes:', err);
      }
    };
    fetchResumes();
  }, []);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const res = await resumeApi.uploadResume(file);
      toast.success('Resume parsed and analyzed successfully!');
      setActiveResume(res.data);
      setShowUploadModal(false);
      // Refresh list
      const allRes = await resumeApi.getResumes();
      setResumes(allRes.data);
    } catch (err: any) {
      console.error('Upload failed:', err);
      const detail = err?.response?.data?.detail;
      let msg = 'Failed to upload and parse resume.';
      if (typeof detail === 'string') {
        msg = detail;
      } else if (Array.isArray(detail)) {
        msg = detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
      } else if (err?.message) {
        msg = err.message;
      }
      toast.error(msg);
      throw new Error(msg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleReScore = async () => {
    if (!activeResume) return;
    setIsScoring(true);
    try {
      const res = await resumeApi.scoreResume(activeResume.id);
      toast.success('Resume score recalculated!');
      setActiveResume({
        ...activeResume,
        quality_score: res.data.overall_score,
        quality_breakdown: res.data as any,
      });
    } catch (err) {
      toast.error('Failed to recalculate score.');
    } finally {
      setIsScoring(false);
    }
  };

  const qualityScore =
    activeResume?.quality_score || (activeResume?.score as any)?.overall_score || 80;
  const qualityBreakdown =
    activeResume?.quality_breakdown || (activeResume?.score as any)?.breakdown || {};
  const tips =
    (activeResume?.quality_breakdown as any)?.tips || (activeResume?.score as any)?.tips || [];

  return (
    <PageWrapper>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Resume Management</h1>
            <p className="text-xs text-slate-500">
              Your parsed profile data used for job-fit scoring and AI enhancement
            </p>
          </div>
          <button
            onClick={() => setShowUploadModal(!showUploadModal)}
            className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition flex items-center gap-1.5 self-start"
          >
            <UploadCloud className="w-4 h-4" />
            {activeResume ? 'Upload New Version' : 'Upload Resume PDF'}
          </button>
        </div>

        {/* Upload Drawer / Box */}
        {(showUploadModal || !activeResume) && (
          <div className="space-y-2">
            <ResumeUpload onUpload={handleUpload} isLoading={isUploading} />
          </div>
        )}

        {/* Resume Health Card */}
        {activeResume && (
          <ResumeScoreCard
            score={qualityScore}
            breakdown={qualityBreakdown}
            tips={tips}
            onReScore={handleReScore}
            isLoading={isScoring}
          />
        )}

        {/* Parsed Resume Details */}
        {activeResume && (
          <div className="space-y-3">
            <h3 className="font-bold text-slate-900 text-sm">Extracted Profile & Skills</h3>
            <ParsedResumeView parsedData={activeResume.parsed_data} />
          </div>
        )}
      </div>
    </PageWrapper>
  );
};
