# Hipe Frontend

Modern, responsive web frontend for the Hipe AI Q&A Agent.

## Features

- 🎨 **Modern UI Design**: Clean, dark-themed interface with smooth interactions
- 🚀 **Fast Performance**: Built with Vite and React 18 for optimal performance
- 📱 **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile
- 🎯 **Real-time Search**: Get instant results from X (Twitter) and Reddit
- 💾 **Local History**: Search history stored in browser localStorage
- 🌙 **Dark Mode**: Built-in dark theme with toggle
- ♿ **Accessible**: WCAG compliant with keyboard navigation support
- 🔍 **Advanced Filters**: Platform, time range, and confidence filters

## Tech Stack

- **Frontend Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Router**: React Router v6
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Markdown Rendering**: Marked

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your API endpoint:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Create a production build:
```bash
npm run build
```

### Preview

Preview the production build locally:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable React components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── SearchInput.tsx
│   │   ├── ResultCard.tsx
│   │   ├── SourcesTable.tsx
│   │   └── Sidebar.tsx
│   ├── pages/            # Page components
│   │   ├── SearchPage.tsx
│   │   ├── HistoryPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── AboutPage.tsx
│   ├── services/         # API and business logic
│   │   └── api.ts
│   ├── store.ts          # Zustand state management
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML template
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Pages

### Search Page (/)
Main search interface with:
- Search input with real-time suggestions
- Filters (platform, time range, confidence)
- AI synthesized answer display
- Confidence and consensus metrics
- Multiple perspectives view
- Source attribution table

### History Page (/history)
- View all previous searches
- Search again with one click
- Clear search history
- Timestamps for each search

### Settings Page (/settings)
- Dark mode toggle
- Default platform preference
- Privacy controls
- Local storage management

### About Page (/about)
- Project information
- Technology stack
- How it works explanation
- FAQ section

## Features in Detail

### Search Interface
- Placeholder with example queries
- Real-time character count
- Keyboard shortcut support (Enter to search)
- Loading state with spinner
- Error handling with user-friendly messages

### Results Display
- Markdown-rendered answer
- Confidence score with color coding
- Consensus level indicator
- Processing time display
- Multiple perspectives in tabs
- Source table with platform badges
- External link support for sources

### Sidebar Filters
- Platform selection (All, X, Reddit)
- Time range options
- Confidence threshold slider
- Recent searches list
- Collapsible sections

## API Integration

The frontend communicates with the backend API at `/api`. Key endpoints:

```
POST /api/search
{
  "query": "string",
  "platform": "string?",
  "time_range": "string?",
  "confidence_threshold": "number?"
}

GET /api/suggestions?q=query
GET /api/history
```

## State Management with Zustand

The app uses Zustand for global state:
- Dark mode toggle
- Search history
- Filter preferences
- Confidence threshold
- Selected platform and time range

All state is persisted to localStorage automatically.

## Responsive Design

- Mobile-first approach
- Breakpoints: 640px (sm), 1024px (md), 1280px (lg)
- Touch-friendly buttons (min 48px height)
- Optimized sidebar collapse on mobile
- Flexible grid layouts

## Accessibility

- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- High contrast ratios (WCAG AA)
- Focus indicators on interactive elements
- Proper heading hierarchy

## Performance Optimizations

- Code splitting with React.lazy()
- Debounced search requests
- Memoized components where appropriate
- Optimized image assets
- Efficient CSS with Tailwind

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

### Environment Variables

For production, set:
```
VITE_API_BASE_URL=https://your-api.com
```

### Build and Serve

```bash
npm run build
npm run preview
```

## Development Guidelines

### Component Creation

```typescript
import React from 'react'

interface Props {
  prop1: string
  prop2?: number
}

export default function ComponentName({ prop1, prop2 }: Props) {
  return <div>Content</div>
}
```

### API Calls

```typescript
import { apiClient } from '../services/api'

const data = await apiClient.search('query')
```

### State Management

```typescript
import { useStore } from '../store'

const { history, addToHistory } = useStore()
```

## Troubleshooting

### CORS Issues
Ensure the backend is running and configured for CORS. Update `vite.config.ts` proxy settings if needed.

### API Connection Errors
- Check `VITE_API_BASE_URL` in `.env`
- Verify backend is running on specified port
- Check browser console for detailed errors

### Build Errors
- Run `npm install` to ensure all dependencies are installed
- Clear node_modules and reinstall if needed
- Check Node.js version (16+ required)

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Write components as functional components
4. Use Tailwind CSS for styling
5. Test responsiveness across devices

## License

MIT - See LICENSE file in root directory

## Support

For issues and questions, please open an issue on the GitHub repository.
