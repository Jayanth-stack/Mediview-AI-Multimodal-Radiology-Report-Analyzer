"use client";

import { useEffect, useRef, useState } from "react";
import StudyViewer from "./StudyViewer";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface UploadFormProps {
  onAnalysisStart: (imageUrl: string, reportText?: string) => void;
}

export default function UploadForm({ onAnalysisStart }: UploadFormProps) {
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
    onAnalysisStart(imageUrl, report);

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
        } catch (err: any) {
          setError(err.message || "Failed to load study");
        }
      })();
    }
  }, [result]);

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm"
        />
      </div>
      <div>
        <textarea
          placeholder="Optional report text"
          value={report}
          onChange={(e) => setReport(e.target.value)}
          className="w-full border rounded p-2 text-sm min-h-[100px]"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p className="text-red-600 text-sm">{error}</p>}
      {jobId && !result && (
        <p className="text-sm text-gray-600">Job: {jobId} (running... {progress}%)</p>
      )}
      {result && (
        <pre className="text-xs bg-white border rounded p-3 overflow-auto max-h-96">
{JSON.stringify(result, null, 2)}
        </pre>
      )}
      {study && <StudyViewer imageSrc={study.image_url} findings={study.findings} />}
    </form>
  );
}

