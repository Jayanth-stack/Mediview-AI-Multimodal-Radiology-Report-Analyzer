"use client";

import { useState } from "react";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) {
      setError("Select an image");
      return;
    }
    const form = new FormData();
    form.append("image", file);
    if (report) form.append("report_text", report);
    setLoading(true);
    try {
      const resp = await fetch(`${backendUrl}/api/analyze`, {
        method: "POST",
        body: form,
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setResult(data);
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

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
      {result && (
        <pre className="text-xs bg-white border rounded p-3 overflow-auto max-h-96">
{JSON.stringify(result, null, 2)}
        </pre>
      )}
    </form>
  );
}

