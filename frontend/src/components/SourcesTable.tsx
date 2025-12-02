import React from 'react'
import { ExternalLink, Twitter } from 'lucide-react'

interface Source {
  platform: string
  author: string
  url: string
  credibility_score: number
  content?: string
}

interface SourcesTableProps {
  sources: Source[]
}

export default function SourcesTable({ sources }: SourcesTableProps) {
  const getPlatformIcon = (platform: string) => {
    if (platform.toLowerCase() === 'x' || platform.toLowerCase() === 'twitter') {
      return <Twitter size={16} className="text-sky-400" />
    }
    return <span className="text-orange-500 font-bold text-sm">R</span>
  }

  const getPlatformColor = (platform: string) => {
    if (platform.toLowerCase() === 'x' || platform.toLowerCase() === 'twitter') {
      return 'bg-sky-900/20 text-sky-200'
    }
    return 'bg-orange-900/20 text-orange-200'
  }

  const getCredibilityColor = (score: number) => {
    if (score > 0.7) return 'text-green-400'
    if (score > 0.4) return 'text-yellow-400'
    return 'text-orange-400'
  }

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-8">
      <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
        <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
        Sources
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Platform</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Author</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300 hidden md:table-cell">Content Preview</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Credibility</th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Link</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((source, idx) => (
              <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                <td className="py-4 px-4">
                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg text-sm font-medium ${getPlatformColor(source.platform)}`}>
                    {getPlatformIcon(source.platform)}
                    {source.platform}
                  </span>
                </td>
                <td className="py-4 px-4 text-sm text-slate-300 font-medium">{source.author}</td>
                <td className="py-4 px-4 text-sm text-slate-400 hidden md:table-cell max-w-xs truncate">
                  {source.content || 'N/A'}
                </td>
                <td className={`py-4 px-4 text-sm font-bold ${getCredibilityColor(source.credibility_score)}`}>
                  {(source.credibility_score * 100).toFixed(0)}%
                </td>
                <td className="py-4 px-4 text-center">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center p-2 hover:bg-slate-700 rounded-lg transition-colors text-slate-400 hover:text-white"
                    title="Open source"
                  >
                    <ExternalLink size={18} />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sources.length > 10 && (
        <div className="mt-4 text-center text-sm text-slate-400">
          Showing top 10 of {sources.length} sources
        </div>
      )}
    </div>
  )
}
