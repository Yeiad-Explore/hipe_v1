import React from 'react'
import { AlertCircle } from 'lucide-react'
import SearchInput from '../components/SearchInput'
import ResultCard from '../components/ResultCard'
import SourcesTable from '../components/SourcesTable'
import Sidebar from '../components/Sidebar'
import { useStore } from '../store'
import { apiClient, SearchResult } from '../services/api'

export default function SearchPage() {
  const [query, setQuery] = React.useState('')
  const [result, setResult] = React.useState<SearchResult | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const {
    history,
    addToHistory,
    selectedPlatform,
    setSelectedPlatform,
    selectedTimeRange,
    setSelectedTimeRange,
    confidenceThreshold,
    setConfidenceThreshold,
  } = useStore()

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const searchResult = await apiClient.search(
        searchQuery,
        selectedPlatform,
        selectedTimeRange,
        confidenceThreshold
      )
      setResult(searchResult)
      addToHistory(searchQuery)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during search'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectRecent = (recentQuery: string) => {
    setQuery(recentQuery)
    handleSearch(recentQuery)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        {!result && (
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Ask the Web
            </h1>
            <p className="text-xl text-slate-400 mb-8">
              Get intelligent answers from X (Twitter) and Reddit with AI-powered synthesis
            </p>
          </div>
        )}

        {/* Search Input */}
        <div className="mb-12">
          <SearchInput
            value={query}
            onChange={setQuery}
            onSubmit={handleSearch}
            loading={loading}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 bg-red-900/20 border border-red-800 rounded-xl p-4 flex items-start gap-4">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <h3 className="font-semibold text-red-400">Search Error</h3>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        {result || loading ? (
          <div className="flex gap-8">
            {/* Sidebar */}
            <div className="hidden lg:block flex-shrink-0 w-80">
              <Sidebar
                onPlatformChange={setSelectedPlatform}
                onTimeRangeChange={setSelectedTimeRange}
                onConfidenceChange={setConfidenceThreshold}
                recentSearches={history.map(h => h.query)}
                onSelectRecent={handleSelectRecent}
                selectedPlatform={selectedPlatform}
                selectedTimeRange={selectedTimeRange}
                confidenceThreshold={confidenceThreshold}
              />
            </div>

            {/* Results */}
            <div className="flex-1 min-w-0">
              {loading ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="w-12 h-12 rounded-full border-4 border-slate-700 border-t-blue-500 animate-spin mb-4"></div>
                  <p className="text-slate-400">Searching X and Reddit...</p>
                  <p className="text-slate-500 text-sm">(This may take 10-30 seconds)</p>
                </div>
              ) : result ? (
                <div className="space-y-8">
                  <ResultCard
                    answer={result.answer}
                    confidence={result.confidence}
                    consensusLevel={result.consensus_level}
                    perspectives={result.perspectives}
                    processingTime={result.processing_time}
                  />

                  {result.sources && result.sources.length > 0 && (
                    <SourcesTable sources={result.sources} />
                  )}
                </div>
              ) : null}
            </div>
          </div>
        ) : (
          // Mobile Sidebar for empty state
          <div className="lg:hidden mb-12">
            <Sidebar
              onPlatformChange={setSelectedPlatform}
              onTimeRangeChange={setSelectedTimeRange}
              onConfidenceChange={setConfidenceThreshold}
              recentSearches={history.map(h => h.query)}
              onSelectRecent={handleSelectRecent}
              selectedPlatform={selectedPlatform}
              selectedTimeRange={selectedTimeRange}
              confidenceThreshold={confidenceThreshold}
            />
          </div>
        )}
      </div>
    </div>
  )
}
