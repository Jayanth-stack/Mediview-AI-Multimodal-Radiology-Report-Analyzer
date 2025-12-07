import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MediViewAI - Intelligent Radiology Analysis',
  description: 'Advanced multimodal radiology analysis powered by AI. Upload medical images and reports for intelligent findings detection.',
  keywords: ['radiology', 'AI', 'medical imaging', 'diagnosis', 'healthcare'],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 text-slate-800 antialiased">
        <main className="relative">{children}</main>
      </body>
    </html>
  )
}
