# Water Management Analytics Hub - React Frontend

A modern, responsive React dashboard for the Water Management multi-flat ranking system. Features real-time leaderboards, analytics with charts, and admin controls.

## 🚀 Features

- **Live Leaderboard & Rankings** - Real-time multi-flat rankings with efficiency scores
- **Analytics Dashboard** - Charts and trends for individual flats
- **Weekly Cumulative Points** - Track points across the entire week
- **Admin Controls** - Day/week reset and simulation mode toggle
- **Real-time Updates** - Auto-refresh with 5-second intervals
- **Beautiful UI** - Modern design with Tailwind CSS and Lucide icons
- **Responsive Design** - Works on desktop, tablet, and mobile

## 📋 Prerequisites

- Node.js 14+ and npm
- Backend API running on `http://localhost:5000`

## 🛠️ Installation

### 1. Setup Frontend

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` to match your API server:

```
REACT_APP_API_URL=http://localhost:5000/api
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements-api.txt
```

## 🎯 Running the Application

### Option 1: Run Both Backend and Frontend

**Terminal 1 - Start Backend API:**

```bash
python api.py
```

The Flask API will start on `http://localhost:5000`

**Terminal 2 - Start React Frontend:**

```bash
cd frontend
npm start
```

The React app will open at `http://localhost:3000`

### Option 2: Production Build

```bash
# Build React app
cd frontend
npm run build

# Serve the build with a production server
npm install -g serve
serve -s build -l 3000
```

## 📊 Dashboard Tabs

### 1. Leaderboard & Rankings

- Real-time daily rankings sorted by efficiency score
- Flat performance metrics (usage, peak flow, status)
- Weekly cumulative points
- Auto-refresh toggle
- Key statistics (total flats, top performer, average efficiency)

### 2. Analytics

- Flat selector to view individual analytics
- Efficiency trend chart (line chart)
- Usage over time (bar chart)
- Detailed statistics (total, average, peak usage)
- Real-time data updates

### 3. Admin

- **Reset Day** - Move to next day and finalize rankings
- **Reset Week** - Clear all points and restart
- **Toggle Simulation** - Switch between simulation/Firebase modes
- System state overview
- Weekly points breakdown

## 🔌 API Endpoints

The React app communicates with the Flask backend via REST API:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check API health |
| `/api/config` | GET | Get app configuration |
| `/api/leaderboard` | GET | Get current rankings |
| `/api/weekly-summary` | GET | Get weekly points |
| `/api/analytics/<flat_id>` | GET | Get flat analytics |
| `/api/flats` | GET | List all flats |
| `/api/admin/reset-day` | POST | Reset to next day |
| `/api/admin/reset-week` | POST | Reset weekly points |
| `/api/admin/toggle-simulation` | POST | Toggle simulation mode |
| `/api/admin/state` | GET | Get system state |

## 🎨 Customization

### Colors

Edit `frontend/tailwind.config.js` to customize the color scheme:

```javascript
colors: {
  primary: { /* primary brand colors */ },
  accent: { 
    green: '#10b981',    // Efficient status
    yellow: '#f59e0b',   // Normal status
    red: '#ef4444',      // High/Penalty status
    purple: '#8b5cf6',   // Admin actions
  }
}
```

### Refresh Rate

To change auto-refresh interval, edit in `frontend/src/components/tabs/LeaderboardTab.jsx`:

```javascript
const interval = setInterval(() => {
  fetchLeaderboard();
  fetchWeeklySummary();
}, 5000); // Change 5000 (5 seconds) to desired milliseconds
```

## 🔗 State Management

The app uses Zustand for global state management:

- `leaderboard` - Current rankings data
- `weeklySummary` - Weekly accumulated points
- `selectedFlat` - Currently selected flat for analytics
- `analytics` - Analytics data for selected flat
- `loading` - Loading state for API calls
- `error` - Error messages

Access state in any component:

```javascript
import useStore from '../store/useStore';

function MyComponent() {
  const { leaderboard, setLeaderboard } = useStore();
  // Use state...
}
```

## 🐛 Troubleshooting

### "Failed to connect to API"

- Ensure Flask backend is running on `http://localhost:5000`
- Check `REACT_APP_API_URL` in `.env`
- Check browser console for CORS errors

### "No data available"

- Start the simulator or ensure readings are being generated
- Click "Refresh" button on Leaderboard tab
- Check backend logs for errors

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

## 📦 Technologies

- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Recharts** - Charts and visualizations
- **Axios** - HTTP client
- **Zustand** - State management
- **Lucide React** - Icons
- **Flask** - Backend API

## 📝 File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx        # Main dashboard component
│   │   └── tabs/
│   │       ├── LeaderboardTab.jsx  # Rankings tab
│   │       ├── AnalyticsTab.jsx    # Analytics tab
│   │       └── AdminTab.jsx        # Admin controls tab
│   ├── services/
│   │   └── api.js              # API client
│   ├── store/
│   │   └── useStore.js         # Zustand store
│   ├── App.jsx                 # Root component
│   └── index.jsx               # Entry point
├── public/
│   └── index.html              # HTML template
├── package.json                # Dependencies
└── tailwind.config.js          # Tailwind configuration
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Heroku

```bash
heroku create your-app-name
git push heroku main
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
EXPOSE 3000
```

## 📄 License

This project is part of the Water Management system and follows the same license.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend logs
3. Check browser console (F12) for errors
4. Ensure all prerequisites are installed
