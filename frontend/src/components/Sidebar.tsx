import React from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface SidebarProps {
  onPlatformChange: (platform: string) => void
  onTimeRangeChange: (range: string) => void
  onConfidenceChange: (value: number) => void
  recentSearches: string[]
  onSelectRecent: (query: string) => void
  selectedPlatform: string
  selectedTimeRange: string
  confidenceThreshold: number
}

export default function Sidebar({
  onPlatformChange,
  onTimeRangeChange,
  onConfidenceChange,
  recentSearches,
  onSelectRecent,
  selectedPlatform,
  selectedTimeRange,
  confidenceThreshold,
}: SidebarProps) {
  const [filtersOpen, setFiltersOpen] = React.useState(true)
  const [recentOpen, setRecentOpen] = React.useState(true)

  const platforms = ['All', 'X (Twitter)', 'Reddit']
  const timeRanges = ['Last 24h', 'Last 7d', 'Last 30d', 'All time']

  return (
    <aside className="w-full md:w-80 bg-slate-800 border-r border-slate-700 rounded-xl">
      {/* Filters Section */}
      <div className="border-b border-slate-700">
        <button
          onClick={() => setFiltersOpen(!filtersOpen)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-700/50 transition-colors"
        >
          <h3 className="font-semibold text-white">Filters</h3>
          {filtersOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>

        {filtersOpen && (
          <div className="px-6 pb-6 space-y-6 border-t border-slate-700">
            {/* Platform Filter */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-3">Platform</label>
              <div className="space-y-2">
                {platforms.map(platform => (
                  <label key={platform} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="radio"
                      name="platform"
                      value={platform}
                      checked={selectedPlatform === platform}
                      onChange={(e) => onPlatformChange(e.target.value)}
                      className="w-4 h-4 rounded border-slate-600 text-blue-600 focus:ring-0 cursor-pointer"
                    />
                    <span className="text-slate-300 text-sm">{platform}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Time Range Filter */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-3">Time Range</label>
              <div className="space-y-2">
                {timeRanges.map(range => (
                  <label key={range} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="radio"
                      name="timeRange"
                      value={range}
                      checked={selectedTimeRange === range}
                      onChange={(e) => onTimeRangeChange(e.target.value)}
                      className="w-4 h-4 rounded border-slate-600 text-blue-600 focus:ring-0 cursor-pointer"
                    />
                    <span className="text-slate-300 text-sm">{range}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Confidence Threshold */}
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-3">
                Confidence Threshold: {(confidenceThreshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={confidenceThreshold}
                onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>
          </div>
        )}
      </div>

      {/* Recent Searches Section */}
      {recentSearches.length > 0 && (
        <div>
          <button
            onClick={() => setRecentOpen(!recentOpen)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-700/50 transition-colors"
          >
            <h3 className="font-semibold text-white">Recent Searches</h3>
            {recentOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>

          {recentOpen && (
            <div className="px-6 pb-6 space-y-2 border-t border-slate-700">
              {recentSearches.slice(0, 10).map((search, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectRecent(search)}
                  className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors truncate"
                  title={search}
                >
                  {search.length > 40 ? search.substring(0, 40) + '...' : search}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
