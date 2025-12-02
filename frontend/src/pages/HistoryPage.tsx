import React from 'react'
import { Trash2, Search } from 'lucide-react'
import { useStore } from '../store'
import { useNavigate } from 'react-router-dom'

export default function HistoryPage() {
  const { history, clearHistory } = useStore()
  const navigate = useNavigate()

  const handleSearch = (query: string) => {
    navigate('/', { state: { initialQuery: query } })
  }

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`

    return date.toLocaleDateString()
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Search History</h1>
          <p className="text-slate-400">
            {history.length === 0 ? 'No searches yet' : `${history.length} searches`}
          </p>
        </div>

        {history.length > 0 ? (
          <>
            <div className="space-y-3 mb-8">
              {history.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex items-center justify-between hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <Search size={20} className="text-slate-500 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="text-white font-medium truncate">{item.query}</p>
                      <p className="text-slate-400 text-sm">{formatDate(item.timestamp)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleSearch(item.query)}
                    className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium flex-shrink-0"
                  >
                    Search Again
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={clearHistory}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/10 hover:bg-red-600/20 text-red-400 hover:text-red-300 border border-red-600/30 rounded-lg transition-colors text-sm font-medium"
            >
              <Trash2 size={16} />
              Clear All History
            </button>
          </>
        ) : (
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-12 text-center">
            <Search size={48} className="text-slate-600 mx-auto mb-4 opacity-50" />
            <p className="text-slate-400 mb-4">No searches yet</p>
            <a
              href="/"
              className="inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Start Searching
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
