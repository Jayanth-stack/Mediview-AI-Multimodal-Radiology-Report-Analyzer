import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MediViewAI',
  description: 'Multimodal Radiology & Report Analyzer',
}

// Placeholder for an icon
const IconPlaceholder = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
  </svg>
);

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-100 text-slate-800">
        <div className="flex h-screen">
          {/* Sidebar */}
          <aside className="w-64 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col">
            <div className="h-16 flex items-center justify-center border-b border-slate-200">
              <h1 className="text-2xl font-bold text-gradient-blue">MediViewAI</h1>
            </div>
            <nav className="flex-1 px-4 py-6 space-y-2">
              <a href="#" className="flex items-center gap-3 px-4 py-2 text-slate-700 font-medium rounded-lg bg-blue-100/60 text-blue-700">
                <IconPlaceholder />
                <span>Dashboard</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-4 py-2 text-slate-500 font-medium rounded-lg hover:bg-slate-100">
                <IconPlaceholder />
                <span>History</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-4 py-2 text-slate-500 font-medium rounded-lg hover:bg-slate-100">
                <IconPlaceholder />
                <span>Settings</span>
              </a>
            </nav>
            <div className="p-4 border-t border-slate-200">
              <button className="btn-primary w-full">New Analysis</button>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto">
            <div className="p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}
