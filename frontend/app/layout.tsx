"use client";
import { motion } from "framer-motion";
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MediViewAI',
  description: 'Multimodal Radiology & Report Analyzer',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <div className="max-w-4xl mx-auto p-6">
          <h1 className="text-2xl font-semibold mb-6">MediViewAI</h1>
          {children}
        </div>
      </body>
    </html>
  )
}

function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6"
            >
              MediViewAI
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl text-slate-600 mb-8 max-w-3xl mx-auto"
            >
              Advanced multimodal radiology analysis powered by AI. Upload medical images and reports for intelligent findings detection.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <button className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-glow transition-all duration-300 transform hover:scale-105">
                Start Analysis
              </button>
              <button className="px-8 py-4 border-2 border-slate-300 text-slate-700 rounded-xl font-semibold hover:border-blue-400 hover:text-blue-600 transition-all duration-300">
                Learn More
              </button>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-4">
              Intelligent Medical Analysis
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Combining computer vision and natural language processing for comprehensive radiology insights
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div 
              whileHover={{ y: -5 }}
              className="medical-highlight p-8 rounded-2xl shadow-soft"
            >
              <div className="w-12 h-12 bg-emerald-500 rounded-xl mb-6 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-3">Automated Detection</h3>
              <p className="text-slate-600">AI-powered identification of anatomical structures and potential abnormalities in medical images.</p>
            </motion.div>

            <motion.div 
              whileHover={{ y: -5 }}
              className="bg-white p-8 rounded-2xl shadow-soft border border-slate-200"
            >
              <div className="w-12 h-12 bg-blue-500 rounded-xl mb-6 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-3">Report Analysis</h3>
              <p className="text-slate-600">Natural language processing of radiology reports to extract key findings and correlate with imaging.</p>
            </motion.div>

            <motion.div 
              whileHover={{ y: -5 }}
              className="bg-white p-8 rounded-2xl shadow-soft border border-slate-200"
            >
              <div className="w-12 h-12 bg-indigo-500 rounded-xl mb-6 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-3">Real-time Processing</h3>
              <p className="text-slate-600">Fast, efficient analysis with live progress tracking and immediate results visualization.</p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Demo Section */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-3xl shadow-soft p-8 md:p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-3xl font-bold text-slate-800 mb-6">
                  See MediViewAI in Action
                </h3>
                <p className="text-lg text-slate-600 mb-8">
                  Upload medical images and optional reports to experience our AI-powered analysis pipeline. Get instant feedback with confidence scores and detailed findings.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                    <span className="text-slate-700">Interactive findings visualization</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-slate-700">Confidence scoring for each detection</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                    <span className="text-slate-700">Real-time progress tracking</span>
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl p-8 text-center">
                  <div className="w-24 h-24 bg-white rounded-2xl shadow-soft mx-auto mb-6 flex items-center justify-center">
                    <svg className="w-12 h-12 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p className="text-slate-600 font-medium">Upload your medical images to get started</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
