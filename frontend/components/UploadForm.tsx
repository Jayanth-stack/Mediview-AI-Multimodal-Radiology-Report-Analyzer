"use client";

import { useEffect, useRef, useState } from "react";
import StudyViewer from "./StudyViewer";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface UploadFormProps {
  onAnalysisComplete: (data: any) => void;
}

export default function UploadForm({ onAnalysisComplete }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [study, setStudy] = useState<any>(null);
  const esRef = useRef<EventSource | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) {
      setError("Select an image");
      return;
    }
    
    const imageUrl = URL.createObjectURL(file);
    // onAnalysisStart(imageUrl, report); // This line is removed as per the new_code

    setLoading(true);
    setProgress(0);
    try {
      // 1) Presign
      const presign = await fetch(`${backendUrl}/api/uploads/presign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, content_type: file.type, use_post: false }),
      });
      if (!presign.ok) throw new Error(`presign HTTP ${presign.status}`);
      const presignData = await presign.json();

      // 2) PUT upload directly to MinIO
      const putResp = await fetch(presignData.url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!putResp.ok) throw new Error(`upload HTTP ${putResp.status}`);

      // 3) Start analyze job
      const startResp = await fetch(`${backendUrl}/api/analyze/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ s3_key: presignData.key, report_text: report || null }),
      });
      if (!startResp.ok) throw new Error(`start HTTP ${startResp.status}`);
      const startData = await startResp.json();
      const jid = startData.job_id;
      setJobId(jid);
      // 4) Prefer SSE for live progress
      try {
        const es = new EventSource(`${backendUrl}/api/jobs/${jid}/events`);
        esRef.current = es;
        es.addEventListener("progress", (ev: MessageEvent) => {
          const data = JSON.parse((ev as MessageEvent).data);
          setProgress(data.progress || 0);
          if (data.status === "completed") {
            setResult(data);
            es.close();
            esRef.current = null;
          } else if (data.status === "failed") {
            setError(data.error || "job failed");
            es.close();
            esRef.current = null;
          }
        });
        es.onerror = () => {
          // Fallback to polling on SSE error
          es.close();
          esRef.current = null;
        };
      } catch {
        // ignore, fallback handled below
      }
      // Fallback polling if SSE didn't attach
      if (!esRef.current) {
        let attempts = 0;
        let final: any = null;
        while (attempts < 60) {
          const st = await fetch(`${backendUrl}/api/jobs/${jid}`);
          const sj = await st.json();
          setProgress(sj.progress || 0);
          if (sj.status === "completed") { final = sj; break; }
          if (sj.status === "failed") { throw new Error(sj.error || "job failed"); }
          await new Promise(r => setTimeout(r, 1000));
          attempts += 1;
        }
        if (!final) throw new Error("timeout waiting for job");
        setResult(final);
      }
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (result?.status === "completed") {
      (async () => {
        try {
          const studyResp = await fetch(`${backendUrl}/api/studies/${result.result.study_id}`);
          if (!studyResp.ok) throw new Error("fetch study failed");
          const studyData = await studyResp.json();
          setStudy(studyData);
          onAnalysisComplete(studyData);
        } catch (err: any) {
          setError(err.message || "Failed to load study");
        }
      })();
    }
  }, [result]);

  if (study) {
    return null; // The parent component will now handle showing the StudyViewer
  }

  return (
    <div className="max-w-xl mx-auto my-12 p-8 border rounded-xl shadow-soft bg-white">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">New Analysis</h2>
      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Upload Radiology Image
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-md">
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-slate-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-slate-600">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                >
                  <span>Upload a file</span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="sr-only"
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-slate-500">{file ? file.name : "PNG, JPG up to 10MB"}</p>
            </div>
          </div>
        </div>
        <div>
          <label htmlFor="report" className="block text-sm font-medium text-slate-700">
            Optional Report Text
          </label>
          <div className="mt-1">
            <textarea
              id="report"
              name="report"
              rows={4}
              placeholder="Paste the radiology report here..."
              value={report}
              onChange={(e) => setReport(e.target.value)}
              className="w-full border-slate-300 rounded-md shadow-sm p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading || !file}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-glow disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {error && <p className="text-red-600 text-sm text-center">{error}</p>}
        {jobId && !result && (
          <div className="w-full bg-slate-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
            <p className="text-sm text-slate-600 text-center mt-2">
              Job: {jobId.substring(0, 8)}... (running... {progress}%)
            </p>
          </div>
        )}
      </form>
    </div>
  );
}

