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

