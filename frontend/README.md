# IGDB Game Recommendation System - Frontend

This is the Next.js 14 frontend for the IGDB Game Recommendation System, built with TypeScript, Tailwind CSS, and shadcn/ui.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx           # Main dashboard page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── games-table.tsx   # Games data table
│   │   ├── data-quality-card.tsx
│   │   ├── budget-card.tsx
│   │   └── collection-stats.tsx
│   ├── lib/                  # Utilities
│   │   ├── utils.ts          # shadcn/ui utilities
│   │   └── mock-data.ts      # Mock data for development
│   └── types/                # TypeScript types
│       └── game.ts           # Game-related types
├── public/                   # Static assets
└── package.json
```

## 🎨 Features

### Current Features
- **Games Table**: Browse and search collected game data
- **Data Quality Dashboard**: View validation reports and statistics
- **Budget Monitoring**: Track GCP credits usage
- **Collection Statistics**: Visualize data with charts and graphs
- **Responsive Design**: Works on desktop and mobile

### Components
- **GamesTable**: Interactive table with search, filtering, and sorting
- **DataQualityCard**: Data validation metrics and issues
- **BudgetCard**: GCP budget tracking and cost optimization tips
- **CollectionStats**: Charts and statistics for data exploration

## 🔌 API Integration

The frontend can work in two modes:

1. **With Backend API**: Connects to FastAPI server at `http://localhost:8000`
2. **Mock Data Mode**: Uses mock data when API is not available

### API Endpoints
- `GET /api/games` - Get all games
- `GET /api/games/{id}` - Get specific game
- `GET /api/games/search?q={query}` - Search games
- `GET /api/data-quality` - Get data quality report
- `GET /api/budget` - Get budget information
- `GET /api/recommendations/{id}` - Get game recommendations

## 🛠️ Development

### Running the Backend
To run with real data, start the FastAPI backend:

```bash
# From the project root
cd /Users/johanenstam/Sync/Utveckling/data-engineering
source venv/bin/activate
python run_api.py
```

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## 🎯 Next Steps

1. **ML Integration**: Add recommendation engine
2. **Real-time Updates**: WebSocket integration for live data
3. **Advanced Filtering**: More sophisticated search and filters
4. **User Interface**: Add user preferences and settings
5. **Performance**: Optimize for large datasets

## 📚 Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **Icons**: Lucide React
- **State Management**: React hooks

## 🔧 Configuration

The app uses mock data by default. To connect to the real API:

1. Start the FastAPI backend server
2. The frontend will automatically detect and connect to the API
3. If the API is not available, it falls back to mock data

## 📱 Responsive Design

The interface is fully responsive and works on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🎨 UI/UX Features

- **Dark/Light Mode**: Automatic theme detection
- **Loading States**: Smooth loading animations
- **Error Handling**: Graceful error messages
- **Accessibility**: Keyboard navigation and screen reader support
- **Performance**: Optimized rendering and data loading