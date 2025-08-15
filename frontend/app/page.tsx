'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import UploadForm from "../components/UploadForm";

interface AnalysisResult {
  id: string;
  timestamp: Date;
  imageUrl: string;
  reportText?: string;
  findings: {
    category: string;
    description: string;
    confidence: 'high' | 'medium' | 'low';
    location?: string;
  }[];
  status: 'processing' | 'completed' | 'error';
}

export default function Page() {
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResult[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAnalysisStart = (imageUrl: string, reportText?: string) => {
    const newAnalysis: AnalysisResult = {
      id: Date.now().toString(),
      timestamp: new Date(),
      imageUrl,
      reportText,
      findings: [],
      status: 'processing'
    };
    
    setCurrentAnalysis(newAnalysis);
    setIsProcessing(true);
    
    // Simulate processing
    setTimeout(() => {
      const completedAnalysis = {
        ...newAnalysis,
        status: 'completed' as const,
        findings: [
          {
            category: 'Chest X-Ray',
            description: 'Normal cardiac silhouette and lung fields',
            confidence: 'high' as const,
            location: 'Bilateral lungs'
          },
          {
            category: 'Bone Structure',
            description: 'No acute fractures identified',
            confidence: 'high' as const,
            location: 'Thoracic cage'
          }
        ]
      };
      
      setCurrentAnalysis(completedAnalysis);
      setAnalysisHistory(prev => [completedAnalysis, ...prev]);
      setIsProcessing(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            Medical Image Analysis
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Upload medical images and reports for AI-powered analysis and findings detection
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-8"
          >
            <h2 className="text-2xl font-semibold text-slate-800 mb-6">Upload & Analyze</h2>
            <UploadForm onAnalysisStart={handleAnalysisStart} />
            
            {/* Processing Status */}
            {isProcessing && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-blue-700 font-medium">Analyzing image...</span>
                </div>
                <div className="mt-3 progress-bar">
                  <div className="progress-fill w-2/3"></div>
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Current Analysis Results */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card p-8"
          >
            <h2 className="text-2xl font-semibold text-slate-800 mb-6">Analysis Results</h2>
            
            {currentAnalysis ? (
              <div className="space-y-6">
                {/* Image Preview */}
                <div className="relative">
                  <img 
                    src={currentAnalysis.imageUrl} 
                    alt="Medical scan" 
                    className="w-full h-48 object-cover rounded-lg border border-slate-200"
                  />
                  <div className="absolute top-2 right-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      currentAnalysis.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                      currentAnalysis.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {currentAnalysis.status}
                    </span>
                  </div>
                </div>

                {/* Findings */}
                {currentAnalysis.findings.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-semibold text-slate-800">Key Findings</h3>
                    {currentAnalysis.findings.map((finding, index) => (
                      <motion.div 
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`p-4 rounded-lg border-l-4 ${
                          finding.confidence === 'high' ? 'bg-emerald-50 border-emerald-400' :
                          finding.confidence === 'medium' ? 'bg-amber-50 border-amber-400' :
                          'bg-rose-50 border-rose-400'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-slate-800">{finding.category}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium confidence-${finding.confidence}`}>
                            {finding.confidence} confidence
                          </span>
                        </div>
                        <p className="text-slate-600 text-sm mb-1">{finding.description}</p>
                        {finding.location && (
                          <p className="text-slate-500 text-xs">Location: {finding.location}</p>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}

                {/* Report Text */}
                {currentAnalysis.reportText && (
                  <div className="bg-slate-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-slate-800 mb-2">Report Text</h3>
                    <p className="text-sm text-slate-600">{currentAnalysis.reportText}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p>Upload an image to see analysis results</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Analysis History */}
        {analysisHistory.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-12 glass-card p-8"
          >
            <h2 className="text-2xl font-semibold text-slate-800 mb-6">Analysis History</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {analysisHistory.map((analysis) => (
                <motion.div 
                  key={analysis.id}
                  whileHover={{ y: -2 }}
                  className="elevated-card p-4 cursor-pointer"
                  onClick={() => setCurrentAnalysis(analysis)}
                >
                  <img 
                    src={analysis.imageUrl} 
                    alt="Analysis" 
                    className="w-full h-32 object-cover rounded-lg mb-3"
                  />
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-slate-800">
                      {analysis.timestamp.toLocaleDateString()}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      analysis.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {analysis.findings.length} findings
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 truncate">
                    {analysis.findings[0]?.description || 'Processing...'}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Quick Stats */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="glass-card p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">{analysisHistory.length}</div>
            <div className="text-slate-600">Total Analyses</div>
          </div>
          <div className="glass-card p-6 text-center">
            <div className="text-3xl font-bold text-emerald-600 mb-2">
              {analysisHistory.filter(a => a.status === 'completed').length}
            </div>
            <div className="text-slate-600">Completed</div>
          </div>
          <div className="glass-card p-6 text-center">
            <div className="text-3xl font-bold text-indigo-600 mb-2">
              {analysisHistory.reduce((acc, a) => acc + a.findings.length, 0)}
            </div>
            <div className="text-slate-600">Total Findings</div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

