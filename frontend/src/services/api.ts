import axios, { AxiosInstance } from 'axios'

export interface SearchResult {
  answer: string
  confidence: number
  consensus_level: string
  perspectives?: Record<string, string>
  sources: Array<{
    platform: string
    author: string
    url: string
    credibility_score: number
    content?: string
  }>
  metadata: {
    num_sources: number
    platforms: Record<string, number>
  }
  processing_time: number
}

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
    })

    // Add request interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error)
        throw error
      }
    )
  }

  async search(
    query: string,
    platform?: string,
    timeRange?: string,
    confidenceThreshold?: number
  ): Promise<SearchResult> {
    try {
      const response = await this.client.post<SearchResult>('/api/search', {
        query,
        platform: platform === 'All' ? undefined : platform,
        time_range: timeRange,
        confidence_threshold: confidenceThreshold,
      })
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Search failed')
      }
      throw error
    }
  }

  async getSuggestions(query: string): Promise<string[]> {
    try {
      const response = await this.client.get<{ suggestions: string[] }>(
        '/api/suggestions',
        { params: { q: query } }
      )
      return response.data.suggestions
    } catch (error) {
      return []
    }
  }

  async getHistory(): Promise<Array<{ query: string; timestamp: string }>> {
    try {
      const response = await this.client.get('/api/history')
      return response.data
    } catch (error) {
      return []
    }
  }
}

export const apiClient = new APIClient()
