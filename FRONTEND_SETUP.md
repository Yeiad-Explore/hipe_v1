# Hipe Frontend - Quick Start Guide

## Overview

The Hipe frontend is a modern React 18 + TypeScript web application with a beautiful dark-themed UI. It provides an intuitive interface for the AI Q&A Agent with features like real-time search, history tracking, and advanced filtering.

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Update `.env` with your backend API URL:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Open your browser to `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
npm run preview
```

## Frontend Features

### Pages

#### Search Page (/)
- **Search Input**: Clean search bar with real-time validation
- **Filters Sidebar**: Filter by platform, time range, and confidence level
- **Results Display**:
  - AI-synthesized answer with markdown support
  - Confidence score with color-coded indicator
  - Consensus level badge
  - Processing time
  - Multiple perspectives in separate sections
  - Full source attribution table

#### History Page (/history)
- View all recent searches with timestamps
- Click "Search Again" to repeat a previous search
- Clear entire history with one click
- Relative time display (e.g., "2 hours ago")

#### Settings Page (/settings)
- Dark mode toggle (currently defaulted to dark)
- Default platform preference
- Privacy settings for local storage
- Analytics consent option
- App information and version

#### About Page (/about)
- Project overview and mission
- Key features highlight
- Technology stack breakdown
- How the AI synthesis works (step-by-step)
- FAQ section with common questions

## Architecture

### Components

```
Header.tsx          - Navigation and branding
Footer.tsx          - Footer with links and copyright
SearchInput.tsx     - Search bar with loading state
ResultCard.tsx      - AI answer and metrics display
SourcesTable.tsx    - Sources with platform badges
Sidebar.tsx         - Filters and recent searches
```

### Pages

```
SearchPage.tsx      - Main search interface
HistoryPage.tsx     - Search history view
SettingsPage.tsx    - User preferences
AboutPage.tsx       - Information and FAQ
```

### Services

```
api.ts              - Axios-based API client with error handling
```

### State Management

```
store.ts            - Zustand store with localStorage persistence
```

## Design System

### Colors

| Token | Color | Usage |
|-------|-------|-------|
| primary | `#3B82F6` (Blue) | Buttons, links, highlights |
| secondary | `#10B981` (Green) | Success states |
| accent | `#F59E0B` (Amber) | Warnings |
| danger | `#EF4444` (Red) | Errors |
| background | `#0F172A` | Main background |
| surface | `#1E293B` | Card backgrounds |
| text | `#F1F5F9` | Primary text |

### Typography

- **Font Family**: Inter, system fonts
- **Base Size**: 16px
- **Scale**: xs (12px) → 3xl (30px)
- **Line Height**: 1.5 (relaxed)

### Spacing

All spacing uses Tailwind's standard scale:
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

### Components

#### SearchInput
```tsx
<SearchInput
  value={query}
  onChange={setQuery}
  onSubmit={handleSearch}
  loading={loading}
  placeholder="Ask anything..."
/>
```

#### ResultCard
```tsx
<ResultCard
  answer="..."
  confidence={0.85}
  consensusLevel="high"
  perspectives={{...}}
  processingTime={12.5}
/>
```

#### SourcesTable
```tsx
<SourcesTable sources={[...]} />
```

## API Integration

### Search Endpoint

```typescript
POST /api/search
{
  "query": "What are people saying about AI?",
  "platform": "All" | "X (Twitter)" | "Reddit",
  "time_range": "Last 24h" | "Last 7d" | "Last 30d" | "All time",
  "confidence_threshold": 0.5
}

Response:
{
  "answer": "markdown formatted answer",
  "confidence": 0.85,
  "consensus_level": "high" | "medium" | "low",
  "perspectives": {
    "consensus": "...",
    "alternative": "...",
    "expert": "..."
  },
  "sources": [
    {
      "platform": "X" | "Reddit",
      "author": "username",
      "url": "https://...",
      "credibility_score": 0.9,
      "content": "preview text"
    }
  ],
  "metadata": {
    "num_sources": 20,
    "platforms": { "X": 15, "Reddit": 5 }
  },
  "processing_time": 12.5
}
```

### Suggestions Endpoint

```typescript
GET /api/suggestions?q=query

Response:
{
  "suggestions": ["suggestion 1", "suggestion 2", ...]
}
```

### History Endpoint

```typescript
GET /api/history

Response:
[
  {
    "query": "search query",
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

## Development Workflow

### Adding a New Page

1. Create component in `src/pages/YourPage.tsx`
2. Add route to `src/App.tsx`
3. Add navigation link to `src/components/Header.tsx`

### Adding a New Component

1. Create component in `src/components/YourComponent.tsx`
2. Use TypeScript interfaces for props
3. Follow existing component patterns

### Making API Calls

```typescript
import { apiClient } from '../services/api'

const result = await apiClient.search('query')
const suggestions = await apiClient.getSuggestions('partial')
```

### Managing Global State

```typescript
import { useStore } from '../store'

const { history, addToHistory, darkMode, toggleDarkMode } = useStore()
```

## Responsive Design

The frontend is built mobile-first and responsive:

- **Mobile** (< 640px): Single column, full-width components
- **Tablet** (640px - 1024px): Two-column with stacked sidebar
- **Desktop** (> 1024px): Three-column with persistent sidebar

Key responsive classes:
```
hidden md:block      - Hide on mobile, show on tablet+
w-full md:w-80       - Full width on mobile, 320px on tablet+
grid-cols-1 md:grid-cols-2 - 1 column on mobile, 2 on tablet+
```

## Performance Optimization

The frontend uses several optimization techniques:

1. **Code Splitting**: Lazy loading pages
2. **Memoization**: React.memo for expensive components
3. **CSS Optimization**: Tailwind JIT compilation
4. **Image Optimization**: Optimized favicons
5. **Caching**: Browser localStorage for history and preferences
6. **Minification**: Production build with Vite

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Port Already in Use

Change the port in `vite.config.ts`:
```typescript
server: {
  port: 3000,
  // ...
}
```

### API Connection Error

1. Verify backend is running on configured port
2. Check `VITE_API_BASE_URL` in `.env`
3. Check browser console for detailed error
4. Ensure CORS is enabled on backend

### Build Fails

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### TypeScript Errors

Ensure TypeScript is up to date:
```bash
npm install -D typescript@latest
```

## Project Statistics

- **Total Components**: 6 reusable components
- **Total Pages**: 4 main pages
- **Lines of Code**: ~2000+
- **Dependencies**: 7 main, 8 dev
- **Build Size**: ~150KB (minified)

## Next Steps

1. ✅ Frontend UI configuration created (`frontend_ui.json`)
2. ✅ React project structure scaffolded
3. ✅ All pages and components built
4. ✅ Styling with Tailwind CSS applied
5. 📝 **Next**: Connect backend API to run full system
6. 🚀 **Deploy**: Build and deploy to production

## Running the Full Stack

To run both backend and frontend:

**Terminal 1 - Backend:**
```bash
cd /
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:5173` in your browser.

## Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Guide](https://vitejs.dev)
- [Zustand](https://github.com/pmndrs/zustand)

## Support

For issues, refer to:
- Frontend README: `frontend/README.md`
- Main project README: `README.md`
- Architecture docs: `ARCHITECTURE.md`
