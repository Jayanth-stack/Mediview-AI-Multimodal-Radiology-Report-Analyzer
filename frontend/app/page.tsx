"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import LandingPage from "../components/LandingPage";
import UploadForm from "../components/UploadForm";
import StudyViewer from "../components/StudyViewer";
import { getToken, removeToken } from "../utils/auth";
import Link from "next/link";

type StudyData = {
  image_url: string;
  findings: any[]; // Replace 'any' with a more specific type if you have one
};

export default function Page() {
  const [view, setView] = useState("landing");
  const [studyData, setStudyData] = useState<StudyData | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
    } else {
      setLoading(false);
    }
  }, [router]);

  const handleLogout = () => {
    removeToken();
    router.push("/login");
  };

  const handleStartAnalysis = () => {
    setView("upload");
  };

  const handleAnalysisComplete = (data: StudyData) => {
    setStudyData(data);
    setView("viewer");
  };

  const handleNewAnalysis = () => {
    setView("upload");
    setStudyData(null);
  }

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  return (
    <div className="relative min-h-screen">
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
        >
          Logout
        </button>
      </div>

      {view === "landing" && <LandingPage onStartAnalysis={handleStartAnalysis} />}

      {view === "upload" && <UploadForm onAnalysisComplete={handleAnalysisComplete} />}

      {view === "viewer" && studyData && (
        <div className="container mx-auto p-4 pt-16">
          <button onClick={handleNewAnalysis} className="mb-4 px-4 py-2 bg-blue-500 text-white rounded">
            New Analysis
          </button>
          <StudyViewer imageSrc={studyData.image_url} findings={studyData.findings} />
        </div>
      )}
    </div>
  );
}

