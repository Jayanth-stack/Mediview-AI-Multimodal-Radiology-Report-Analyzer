"use client";
import { useState } from "react";
import LandingPage from "../components/LandingPage";
import UploadForm from "../components/UploadForm";
import StudyViewer from "../components/StudyViewer";

type StudyData = {
  image_url: string;
  findings: any[]; // Replace 'any' with a more specific type if you have one
};

export default function Page() {
  const [view, setView] = useState("landing");
  const [studyData, setStudyData] = useState<StudyData | null>(null);

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

  if (view === "landing") {
    return <LandingPage onStartAnalysis={handleStartAnalysis} />;
  }
  if (view === "upload") {
    return <UploadForm onAnalysisComplete={handleAnalysisComplete} />;
  }
  if (view === "viewer" && studyData) {
    return (
      <div className="container mx-auto p-4">
        <button onClick={handleNewAnalysis} className="mb-4 px-4 py-2 bg-blue-500 text-white rounded">
          New Analysis
        </button>
        <StudyViewer imageSrc={studyData.image_url} findings={studyData.findings} />
      </div>
    );
  }

  return <LandingPage onStartAnalysis={handleStartAnalysis} />;
}

