import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface HistoryItem {
  query: string
  timestamp: number
}

interface StoreState {
  darkMode: boolean
  toggleDarkMode: () => void
  history: HistoryItem[]
  addToHistory: (query: string) => void
  clearHistory: () => void
  selectedPlatform: string
  setSelectedPlatform: (platform: string) => void
  selectedTimeRange: string
  setSelectedTimeRange: (range: string) => void
  confidenceThreshold: number
  setConfidenceThreshold: (threshold: number) => void
}

export const useStore = create<StoreState>()(
  persist(
    (set) => ({
      darkMode: true,
      toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),

      history: [],
      addToHistory: (query: string) =>
        set((state) => ({
          history: [
            { query, timestamp: Date.now() },
            ...state.history.slice(0, 49), // Keep last 50
          ],
        })),
      clearHistory: () => set({ history: [] }),

      selectedPlatform: 'All',
      setSelectedPlatform: (platform: string) => set({ selectedPlatform: platform }),

      selectedTimeRange: 'Last 7d',
      setSelectedTimeRange: (range: string) => set({ selectedTimeRange: range }),

      confidenceThreshold: 0.5,
      setConfidenceThreshold: (threshold: number) => set({ confidenceThreshold: threshold }),
    }),
    {
      name: 'hipe-store',
    }
  )
)
