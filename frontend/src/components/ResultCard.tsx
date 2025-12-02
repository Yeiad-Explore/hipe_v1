import React from 'react'
import { ExternalLink, AlertCircle } from 'lucide-react'
import { marked } from 'marked'

interface ResultCardProps {
  answer: string
  confidence: number
  consensusLevel: string
  perspectives?: Record<string, string>
  processingTime: number
}

export default function ResultCard({
  answer,
  confidence,
  consensusLevel,
  perspectives,
  processingTime,
}: ResultCardProps) {
  const getConfidenceColor = (conf: number) => {
    if (conf > 0.7) return 'bg-green-900 text-green-200'
    if (conf > 0.4) return 'bg-yellow-900 text-yellow-200'
    return 'bg-red-900 text-red-200'
  }

  const getConsensusColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'text-green-400'
      case 'medium': return 'text-yellow-400'
      case 'low': return 'text-orange-400'
      default: return 'text-slate-400'
    }
  }

  const htmlContent = marked(answer, { breaks: true })

  return (
    <div className="space-y-6">
      {/* Main Answer */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-8">
        <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
          AI Synthesis
        </h2>
        <div
          className="prose prose-invert max-w-none text-slate-300 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div className="text-sm text-slate-400 mb-2">Confidence Score</div>
          <div className={`flex items-center gap-3 ${getConfidenceColor(confidence)} px-3 py-2 rounded-lg w-fit`}>
            <div className="text-2xl font-bold">{(confidence * 100).toFixed(0)}%</div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div className="text-sm text-slate-400 mb-2">Consensus Level</div>
          <div className={`text-2xl font-bold ${getConsensusColor(consensusLevel)}`}>
            {consensusLevel.charAt(0).toUpperCase() + consensusLevel.slice(1)}
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <div className="text-sm text-slate-400 mb-2">Processing Time</div>
          <div className="text-2xl font-bold text-slate-100">
            {processingTime.toFixed(2)}s
          </div>
        </div>
      </div>

      {/* Perspectives */}
      {perspectives && Object.keys(perspectives).length > 0 && (
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-8">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
            Multiple Perspectives
          </h3>
          <div className="space-y-4">
            {Object.entries(perspectives).map(([key, value]) => (
              <div key={key} className="border-l-4 border-slate-600 pl-4 py-2">
                <div className="text-sm font-semibold text-slate-300 mb-2">
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </div>
                <div className="text-slate-400 text-sm leading-relaxed">{value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
