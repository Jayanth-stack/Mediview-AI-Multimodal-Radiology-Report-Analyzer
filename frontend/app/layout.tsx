import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MediViewAI',
  description: 'Multimodal Radiology & Report Analyzer',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-100 text-slate-800">
        <main>{children}</main>
      </body>
    </html>
  )
}
