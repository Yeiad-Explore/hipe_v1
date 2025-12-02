# Hipe Frontend - Components Documentation

## Overview

This document provides detailed documentation for all React components in the Hipe frontend.

## Reusable Components

### 1. Header

**Location**: `src/components/Header.tsx`

**Purpose**: Navigation header with logo, navigation links, and action buttons

**Features**:
- Sticky positioning
- Mobile-responsive hamburger menu
- Dark mode toggle
- Logo with gradient background
- Active link indicators

**Props**: None (uses internal state)

**Usage**:
```tsx
import Header from './components/Header'

// In App.tsx
<Header />
```

**Responsive Behavior**:
- Desktop: Horizontal navigation visible
- Mobile: Navigation in hamburger menu

### 2. Footer

**Location**: `src/components/Footer.tsx`

**Purpose**: Footer with company info, links, and social media

**Features**:
- Three-column layout (desktop)
- Single-column responsive
- Social media icons
- Current year display
- Copyright information

**Props**: None

**Usage**:
```tsx
import Footer from './components/Footer'

<Footer />
```

### 3. SearchInput

**Location**: `src/components/SearchInput.tsx`

**Purpose**: Search bar with validation and loading state

**Props**:
```typescript
interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: (value: string) => void
  loading?: boolean
  placeholder?: string
}
```

**Features**:
- Real-time input validation
- Loading spinner during search
- Enter key submission
- Disabled state when loading
- Search icon
- Example placeholder text

**Usage**:
```tsx
import SearchInput from './components/SearchInput'

const [query, setQuery] = useState('')
const [loading, setLoading] = useState(false)

<SearchInput
  value={query}
  onChange={setQuery}
  onSubmit={handleSearch}
  loading={loading}
  placeholder="Ask anything..."
/>
```

**Keyboard Support**:
- `Enter`: Submit search
- `Disabled`: While loading

### 4. ResultCard

**Location**: `src/components/ResultCard.tsx`

**Purpose**: Display AI-synthesized answer with confidence metrics

**Props**:
```typescript
interface ResultCardProps {
  answer: string
  confidence: number
  consensusLevel: string
  perspectives?: Record<string, string>
  processingTime: number
}
```

**Features**:
- Markdown rendering of answer
- Color-coded confidence badge
  - Green: > 70%
  - Yellow: 40-70%
  - Red: < 40%
- Consensus level indicator
- Processing time display
- Perspectives in collapsible sections
- Border accent color

**Usage**:
```tsx
import ResultCard from './components/ResultCard'

<ResultCard
  answer="The answer in markdown format..."
  confidence={0.85}
  consensusLevel="high"
  perspectives={{
    consensus: "Most sources agree...",
    alternative: "Some sources suggest...",
    expert: "Experts note..."
  }}
  processingTime={12.5}
/>
```

**Markdown Support**:
Supports standard markdown:
- `**bold**`
- `*italic*`
- `# Headers`
- `- Lists`
- `[Links](url)`

### 5. SourcesTable

**Location**: `src/components/SourcesTable.tsx`

**Purpose**: Display sources with platform badges and credibility scores

**Props**:
```typescript
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
```

**Features**:
- Platform-specific badges (X, Reddit)
- Credibility score color coding
- External link button
- Hover effects
- Responsive table (hides content on mobile)
- Truncated long content
- Shows top 10 of N sources message

**Usage**:
```tsx
import SourcesTable from './components/SourcesTable'

<SourcesTable
  sources={[
    {
      platform: "X",
      author: "@username",
      url: "https://twitter.com/...",
      credibility_score: 0.9,
      content: "Tweet text preview..."
    },
    // ...
  ]}
/>
```

**Credibility Color Coding**:
- Green: > 70%
- Yellow: 40-70%
- Orange: < 40%

### 6. Sidebar

**Location**: `src/components/Sidebar.tsx`

**Purpose**: Filters and recent searches sidebar

**Props**:
```typescript
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
```

**Features**:
- **Filters Section**:
  - Platform selection (radio buttons)
  - Time range selection (radio buttons)
  - Confidence threshold slider
  - Collapsible section

- **Recent Searches Section**:
  - List of last 10 searches
  - One-click re-search
  - Truncated long queries
  - Collapsible section

**Usage**:
```tsx
import Sidebar from './components/Sidebar'

<Sidebar
  onPlatformChange={setPlatform}
  onTimeRangeChange={setTimeRange}
  onConfidenceChange={setConfidence}
  recentSearches={history}
  onSelectRecent={handleSelectRecent}
  selectedPlatform={platform}
  selectedTimeRange={timeRange}
  confidenceThreshold={confidence}
/>
```

**Filter Options**:
- **Platforms**: All, X (Twitter), Reddit
- **Time Range**: Last 24h, Last 7d, Last 30d, All time
- **Confidence**: 0 to 1 (slider)

## Page Components

### SearchPage

**Location**: `src/pages/SearchPage.tsx`

**Purpose**: Main search interface with results display

**Features**:
- Hero section when no results
- Error handling with alert display
- Loading state with spinner
- Sidebar + Results layout
- Mobile-responsive layout
- Search history integration
- Filter state management

### HistoryPage

**Location**: `src/pages/HistoryPage.tsx`

**Purpose**: View and manage search history

**Features**:
- List of all searches with timestamps
- "Search Again" button for each
- Clear history button
- Relative time display
- Empty state with CTA
- Search count display

### SettingsPage

**Location**: `src/pages/SettingsPage.tsx`

**Purpose**: User preferences and configuration

**Sections**:
1. **Appearance**: Dark mode toggle
2. **Search Preferences**: Default platform
3. **Privacy**: Data collection settings
4. **About**: Version info, tech stack

### AboutPage

**Location**: `src/pages/AboutPage.tsx`

**Purpose**: Project information and FAQ

**Sections**:
1. **Mission**: Project description
2. **Features**: Key capabilities
3. **Technology Stack**: Frontend and backend tech
4. **How It Works**: Step-by-step process
5. **FAQ**: Common questions

## State Management (Zustand)

**Location**: `src/store.ts`

**Store State**:
```typescript
interface StoreState {
  // Dark mode
  darkMode: boolean
  toggleDarkMode: () => void

  // History
  history: HistoryItem[]
  addToHistory: (query: string) => void
  clearHistory: () => void

  // Filters
  selectedPlatform: string
  setSelectedPlatform: (platform: string) => void
  selectedTimeRange: string
  setSelectedTimeRange: (range: string) => void
  confidenceThreshold: number
  setConfidenceThreshold: (threshold: number) => void
}
```

**Usage**:
```tsx
import { useStore } from '../store'

const { darkMode, toggleDarkMode, history } = useStore()
```

**Persistence**:
- All state automatically persisted to localStorage
- Key: `hipe-store`
- Loaded on app startup

## API Service

**Location**: `src/services/api.ts`

**Main Client**: `APIClient`

**Methods**:
```typescript
// Search
search(
  query: string,
  platform?: string,
  timeRange?: string,
  confidenceThreshold?: number
): Promise<SearchResult>

// Suggestions
getSuggestions(query: string): Promise<string[]>

// History
getHistory(): Promise<Array<{ query: string; timestamp: string }>>
```

**Error Handling**:
- Axios interceptors for response handling
- User-friendly error messages
- Automatic error logging

**Usage**:
```tsx
import { apiClient } from '../services/api'

const result = await apiClient.search('query')
const suggestions = await apiClient.getSuggestions('part')
```

## Styling

### Tailwind Classes

**Common Utilities**:
```
// Layout
flex, grid, gap, p-*, m-*

// Colors
bg-slate-*, text-*, border-*

// Effects
rounded-*, shadow-*, opacity-*

// Responsive
sm:, md:, lg:, xl:

// States
hover:, focus:, disabled:, active:
```

### Custom CSS

**Location**: `src/index.css`

**Features**:
- Global Tailwind imports
- Custom scrollbar styling
- Prose styling for markdown
- Badge and card utilities
- Responsive utilities

## Component Hierarchy

```
App
├── Header
│   ├── Navigation links
│   └── Dark mode toggle
├── Routes
│   ├── SearchPage
│   │   ├── SearchInput
│   │   ├── Sidebar
│   │   └── Results
│   │       ├── ResultCard
│   │       └── SourcesTable
│   ├── HistoryPage
│   ├── SettingsPage
│   └── AboutPage
└── Footer
```

## Best Practices

### Creating Components

1. Use functional components
2. Define prop interfaces
3. Use TypeScript for type safety
4. Add JSDoc comments for documentation
5. Keep components focused and reusable

### Component Template

```tsx
import React from 'react'

interface ComponentProps {
  prop1: string
  prop2?: number
}

/**
 * Component description
 * @param prop1 - Description
 * @param prop2 - Optional description
 */
export default function ComponentName({ prop1, prop2 }: ComponentProps) {
  return (
    <div className="...">
      {/* Component content */}
    </div>
  )
}
```

### Styling

1. Use Tailwind CSS classes
2. Keep styling in className
3. Use custom CSS only when necessary
4. Follow existing color scheme
5. Maintain consistent spacing

### State Management

1. Use Zustand for global state
2. Use React hooks for local state
3. Keep state as high as needed
4. Persist important state to localStorage

## Accessibility

- Semantic HTML (button, form, nav, etc.)
- ARIA labels where needed
- Keyboard navigation support
- High contrast ratios
- Focus indicators on interactive elements
- Screen reader friendly

## Testing Components

Each component is independent and testable:

```tsx
import { render, screen } from '@testing-library/react'
import SearchInput from './SearchInput'

test('renders search input', () => {
  render(<SearchInput value="" onChange={() => {}} onSubmit={() => {}} />)
  expect(screen.getByPlaceholderText(/ask anything/i)).toBeInTheDocument()
})
```

## Component Examples

### Using SearchInput in Custom Component

```tsx
import SearchInput from './components/SearchInput'
import { useState } from 'react'

export default function MySearchComponent() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSearch = async (q: string) => {
    setLoading(true)
    try {
      // Perform search
    } finally {
      setLoading(false)
    }
  }

  return (
    <SearchInput
      value={query}
      onChange={setQuery}
      onSubmit={handleSearch}
      loading={loading}
    />
  )
}
```

### Using Result Components Together

```tsx
import ResultCard from './components/ResultCard'
import SourcesTable from './components/SourcesTable'

export default function ResultsDisplay({ data }) {
  return (
    <div className="space-y-8">
      <ResultCard
        answer={data.answer}
        confidence={data.confidence}
        consensusLevel={data.consensus_level}
        perspectives={data.perspectives}
        processingTime={data.processing_time}
      />
      <SourcesTable sources={data.sources} />
    </div>
  )
}
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release |

## Support

For questions about components, refer to:
- Individual component files
- `src/` directory structure
- Frontend README
- TypeScript interfaces
