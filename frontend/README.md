# Highway Monitoring Dashboard

A high-fidelity, modern Smart City Traffic Control Dashboard built with React and Tailwind CSS.

## Features

- 🎨 Dark futuristic UI with glassmorphism effects
- 📹 CCTV camera feed grid with live indicators
- 📊 Real-time traffic analytics with animated progress bars
- 🚨 Alert management system with severity levels
- 🎤 Floating microphone button for voice commands
- 📱 Fully responsive design (desktop-first)

## Tech Stack

- React 18 (Functional Components)
- Tailwind CSS 3.4
- Vite 5
- PostCSS & Autoprefixer

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
highway-monitoring-dashboard/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Fixed header with title and controls
│   │   ├── Sidebar.jsx         # Left sidebar with area division and alerts
│   │   ├── AlertCard.jsx       # Reusable alert card component
│   │   ├── CameraFeed.jsx      # CCTV camera feed component
│   │   └── AnalyticsBar.jsx    # Traffic analytics progress bar
│   ├── App.jsx                 # Main application component
│   ├── main.jsx                # React entry point
│   └── index.css               # Tailwind directives and global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Color Theme

- **Primary**: Deep Blue / Navy Gradient (#0a1929, #1a2332)
- **Accent**: Electric Blue (#00d4ff) + Green (#00ff88)
- **Alerts**: Red (High), Yellow (Medium), Blue (Low)
- **Text**: White & Light Gray

## Components

### Header
Fixed top header with dashboard title, LIVE SYSTEM badge, and close button.

### Sidebar
Fixed left sidebar containing:
- Area Division buttons (Entrance, Flyover, Bridge, Lanes, Exit)
- Recent Alerts section with severity badges
- Preview All Alerts button

### Camera Feed Grid
2x2 grid of CCTV camera feeds with:
- LIVE and REC indicators
- Camera ID and location
- Alert detection overlay (one camera shows alert)

### Traffic Analytics
Animated progress bars showing:
- Vehicle Count (vehicles/hr)
- Average Speed (MPH)
- Traffic Flow Efficiency (%)

### Real-Time Flux Chart
Bar-style analytics graph showing traffic patterns over time.

## Notes

- This is a static frontend-only application (no backend)
- All data is dummy/placeholder data
- Camera feeds use gradient placeholders
- Chart is visual-only (no real data binding)

