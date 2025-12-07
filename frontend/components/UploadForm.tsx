"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface UploadFormProps {
  onAnalysisComplete: (data: any) => void;
}

export default function UploadForm({ onAnalysisComplete }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [progressStage, setProgressStage] = useState<string>("");
  const [study, setStudy] = useState<any>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const esRef = useRef<EventSource | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Generate file preview
  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }
    setPreview(null);
  }, [file]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith("image/")) {
      setFile(droppedFile);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) {
      setError("Please select a medical image to analyze");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      setError("Session expired. Please login again.");
      return;
    }

    setLoading(true);
    setProgress(0);
    setProgressStage("Preparing upload...");

    try {
      // 1) Presign
      setProgressStage("Getting upload credentials...");
      const presign = await fetch(`${backendUrl}/api/uploads/presign`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          filename: file.name,
          content_type: file.type,
          use_post: false,
        }),
      });
      if (!presign.ok) throw new Error(`Upload preparation failed`);
      const presignData = await presign.json();
      setProgress(15);

      // 2) PUT upload
      setProgressStage("Uploading image...");
      const putResp = await fetch(presignData.url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!putResp.ok) throw new Error(`Image upload failed`);
      setProgress(35);

      // 3) Start analyze job
      setProgressStage("Initializing AI analysis...");
      const startResp = await fetch(`${backendUrl}/api/analyze/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          s3_key: presignData.key,
          report_text: report || null,
        }),
      });
      if (!startResp.ok) throw new Error(`Analysis start failed`);
      const startData = await startResp.json();
      const jid = startData.job_id;
      setJobId(jid);
      setProgress(45);

      // 4) SSE or Polling
      setProgressStage("Running AI analysis...");
      try {
        const es = new EventSource(
          `${backendUrl}/api/jobs/${jid}/events?token=${token}`
        );
        esRef.current = es;
        es.addEventListener("progress", (ev: MessageEvent) => {
          const data = JSON.parse(ev.data);
          const newProgress = 45 + (data.progress || 0) * 0.55;
          setProgress(newProgress);
          if (data.status === "completed") {
            setResult(data);
            setProgressStage("Analysis complete!");
            es.close();
            esRef.current = null;
          } else if (data.status === "failed") {
            setError(data.error || "Analysis failed");
            es.close();
            esRef.current = null;
          }
        });
        es.onerror = () => {
          es.close();
          esRef.current = null;
        };
      } catch {
        // Fallback polling
      }

      // Fallback polling
      if (!esRef.current) {
        let attempts = 0;
        let final: any = null;
        while (attempts < 60) {
          const st = await fetch(`${backendUrl}/api/jobs/${jid}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          const sj = await st.json();
          const newProgress = 45 + (sj.progress || 0) * 0.55;
          setProgress(newProgress);
          if (sj.status === "completed") {
            final = sj;
            break;
          }
          if (sj.status === "failed") {
            throw new Error(sj.error || "Analysis failed");
          }
          await new Promise((r) => setTimeout(r, 1000));
          attempts += 1;
        }
        if (!final) throw new Error("Analysis timeout");
        setResult(final);
        setProgressStage("Analysis complete!");
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
          const token = localStorage.getItem("token");
          const studyResp = await fetch(
            `${backendUrl}/api/studies/${result.result.study_id}`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          if (!studyResp.ok) throw new Error("Failed to load results");
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
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 py-12 px-4">
      {/* Background Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ x: [0, 30, 0], y: [0, -20, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-20 right-20 w-72 h-72 bg-gradient-to-r from-purple-200/30 to-pink-200/30 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ x: [0, -20, 0], y: [0, 30, 0] }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-40 left-20 w-80 h-80 bg-gradient-to-r from-blue-200/30 to-cyan-200/30 rounded-full blur-3xl"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative max-w-2xl mx-auto"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4 shadow-lg shadow-purple-500/25"
          >
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </motion.div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">New Analysis</h1>
          <p className="text-slate-600">Upload a medical image for AI-powered analysis</p>
        </div>

        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 p-8"
        >
          <form onSubmit={onSubmit} className="space-y-6">
            {/* Drag & Drop Zone */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-3">
                Medical Image
              </label>
              <motion.div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current?.click()}
                animate={{
                  borderColor: isDragOver ? "#8b5cf6" : file ? "#10b981" : "#e2e8f0",
                  backgroundColor: isDragOver ? "rgba(139, 92, 246, 0.05)" : file ? "rgba(16, 185, 129, 0.05)" : "rgba(248, 250, 252, 0.5)",
                }}
                className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${isDragOver ? "scale-[1.02]" : ""
                  }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="hidden"
                />

                <AnimatePresence mode="wait">
                  {preview ? (
                    <motion.div
                      key="preview"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      className="space-y-4"
                    >
                      <div className="relative inline-block">
                        <img
                          src={preview}
                          alt="Preview"
                          className="max-h-48 rounded-xl shadow-lg mx-auto"
                        />
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute -top-2 -right-2 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg"
                        >
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </motion.div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-700">{file?.name}</p>
                        <p className="text-xs text-slate-500">
                          {file && (file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFile(null);
                        }}
                        className="text-sm text-red-500 hover:text-red-600 font-medium"
                      >
                        Remove & choose different file
                      </button>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="dropzone"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="space-y-3"
                    >
                      <motion.div
                        animate={{ y: isDragOver ? -5 : 0 }}
                        className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center"
                      >
                        <svg className="w-8 h-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </motion.div>
                      <div>
                        <p className="text-slate-600">
                          <span className="text-purple-600 font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-sm text-slate-400 mt-1">
                          PNG, JPG, DICOM up to 50MB
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </div>

            {/* Report Text */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-3">
                Clinical Context <span className="font-normal text-slate-400">(Optional)</span>
              </label>
              <textarea
                value={report}
                onChange={(e) => setReport(e.target.value)}
                rows={4}
                placeholder="Add any relevant clinical history, symptoms, or prior findings..."
                className="w-full px-4 py-3 bg-slate-50/50 border border-slate-200 rounded-xl text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400 transition-all duration-200 resize-none"
              />
            </div>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Progress Bar */}
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-600 font-medium">{progressStage}</span>
                      <span className="text-purple-600 font-semibold">{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full relative"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                      </motion.div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={loading || !file}
              whileHover={{ scale: loading || !file ? 1 : 1.01 }}
              whileTap={{ scale: loading || !file ? 1 : 0.99 }}
              className={`w-full py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${loading || !file
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40"
                }`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Analyzing...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  Start AI Analysis
                </span>
              )}
            </motion.button>
          </form>
        </motion.div>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-slate-500">
            💡 <span className="font-medium">Tip:</span> For best results, use high-resolution images and provide clinical context
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
