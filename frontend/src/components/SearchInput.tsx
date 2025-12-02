import React from 'react'
import { Search, Loader } from 'lucide-react'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: (value: string) => void
  loading?: boolean
  placeholder?: string
}

export default function SearchInput({
  value,
  onChange,
  onSubmit,
  loading = false,
  placeholder = "Ask anything... What are people saying about...",
}: SearchInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      onSubmit(value)
    }
  }

  return (
    <div className="relative">
      <div className="relative flex items-center">
        <Search className="absolute left-4 text-slate-400 pointer-events-none" size={20} />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-12 pr-14 py-4 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
          disabled={loading}
        />
        <button
          onClick={() => onSubmit(value)}
          disabled={loading || !value.trim()}
          className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          title="Search"
        >
          {loading ? (
            <Loader size={20} className="animate-spin" />
          ) : (
            <Search size={20} />
          )}
        </button>
      </div>
    </div>
  )
}
