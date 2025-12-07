"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import LandingPage from "../components/LandingPage";
import UploadForm from "../components/UploadForm";
import StudyViewer from "../components/StudyViewer";
import { getToken, removeToken } from "../utils/auth";

type View = "landing" | "upload" | "viewer";

interface StudyData {
  id: number;
  s3_key: string;
  modality?: string;
  report?: any;
  findings?: any[];
}

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>("landing");
  const [studyData, setStudyData] = useState<StudyData | null>(null);

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
  };

  const handleBackToHome = () => {
    setView("landing");
    setStudyData(null);
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 mx-auto mb-4"
          >
            <div className="w-full h-full border-4 border-purple-500/30 border-t-purple-500 rounded-full" />
          </motion.div>
          <p className="text-white/60 text-lg">Loading MediViewAI...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen">
      {/* Navigation Bar */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 left-0 right-0 z-50"
      >
        <div className="mx-4 mt-4">
          <div className="max-w-7xl mx-auto px-6 py-3 bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-100">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <button
                onClick={handleBackToHome}
                className="flex items-center gap-3 hover:opacity-80 transition-opacity"
              >
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  MediViewAI
                </span>
              </button>

              {/* Navigation Links */}
              <div className="hidden md:flex items-center gap-6">
                <button
                  onClick={handleBackToHome}
                  className={`text-sm font-medium transition-colors ${view === "landing" ? "text-purple-600" : "text-slate-600 hover:text-purple-600"
                    }`}
                >
                  Home
                </button>
                <button
                  onClick={handleStartAnalysis}
                  className={`text-sm font-medium transition-colors ${view === "upload" ? "text-purple-600" : "text-slate-600 hover:text-purple-600"
                    }`}
                >
                  New Analysis
                </button>
              </div>

              {/* User Menu */}
              <div className="flex items-center gap-4">
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all duration-200"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="pt-24">
        <AnimatePresence mode="wait">
          {view === "landing" && (
            <motion.div
              key="landing"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <LandingPage onStartAnalysis={handleStartAnalysis} />
            </motion.div>
          )}

          {view === "upload" && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <UploadForm onAnalysisComplete={handleAnalysisComplete} />
            </motion.div>
          )}

          {view === "viewer" && studyData && (
            <motion.div
              key="viewer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 py-8 px-4"
            >
              <div className="max-w-7xl mx-auto">
                <div className="mb-6 flex items-center gap-4">
                  <button
                    onClick={handleNewAnalysis}
                    className="flex items-center gap-2 px-4 py-2.5 bg-white/80 backdrop-blur-sm border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-white hover:border-purple-200 transition-all duration-200 shadow-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Analysis
                  </button>
                  <button
                    onClick={handleBackToHome}
                    className="flex items-center gap-2 px-4 py-2.5 text-slate-600 hover:text-purple-600 font-medium transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Back to Home
                  </button>
                </div>
                <StudyViewer study={studyData} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
