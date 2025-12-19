# Transport Delay Predictor - Frontend

A clean, professional, and accessible web application for predicting transport delays using AI-powered machine learning models.

## Features

- **Clean & Minimal Design**: Focus on functionality without visual clutter
- **Professional UI**: Corporate-friendly color scheme and typography
- **Intuitive Interface**: Self-explanatory interface requiring no tutorial
- **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **Accessibility First**: WCAG 2.1 AA compliant with full keyboard navigation and screen reader support
- **Feature Importance Visualization**: Optional bar chart showing top contributing factors
- **Smooth Animations**: Staggered animations, bounce effects, and smooth transitions
- **Performance Optimized**: Debounced validation, optimized rendering

## Project Structure

```
frontAI/
├── index.html          # Main HTML structure
├── css/
│   └── styles.css      # All styles (variables, components, responsive)
├── js/
│   ├── app.js          # Main application logic
│   └── api.js          # API integration module
└── README.md           # This file
```

## Getting Started

### Quick Start (Recommended)

**Linux/Mac:**
```bash
./start.sh          # Start both frontend and backend
```

**Windows:**
```cmd
start_backend.bat    # Start backend (in one terminal)
start_frontend.bat   # Start frontend (in another terminal)
```

**Or use individual scripts:**
```bash
./start_backend.sh   # Backend only
./start_frontend.sh  # Frontend only
```

See `QUICK_START.md` for more details!

### Prerequisites

- **Python 3.9+** (for backend and frontend server)
- A modern web browser (Chrome, Firefox, Safari, Edge)
- Backend API running (automatically started by scripts)

### Manual Setup

1. **Start Backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 5000
   ```

2. **Start Frontend:**
   ```bash
   python3 -m http.server 8000
   ```

3. **Access:**
   - Frontend: http://localhost:8000
   - Backend API Docs: http://localhost:5000/docs

## Development Phases

### ✅ Phase 1: Setup (Completed)
- [x] Project structure created
- [x] Base HTML structure
- [x] CSS variables and reset
- [x] Base styling

### ✅ Phase 2: Static UI (Completed)
- [x] Header component
- [x] Input form layout
- [x] All form elements styled
- [x] Results card layout
- [x] Responsive design

### ✅ Phase 3: Functionality (Completed)
- [x] Complete form validation logic with all edge cases
- [x] Full API integration with error handling
- [x] Loading states with animations
- [x] Toast notification system for errors
- [x] Complete results display logic

### ✅ Phase 4: Polish (Completed)
- [x] Enhanced animations and transitions (staggered, bounce effects)
- [x] Feature importance visualization (optional)
- [x] Skip to main content link for accessibility
- [x] Enhanced keyboard navigation (arrow keys for radio buttons)
- [x] Performance optimizations (debounced validation, optimized animations)
- [x] Better focus management

## Form Fields

- **Route ID**: Number input (1-10)
- **Weather Condition**: Dropdown (Clear, Cloudy, Rainy, Snowy)
- **Passenger Count**: Number input with +/- buttons (0-500, step 10)
- **Time of Day**: Radio buttons (Morning, Afternoon, Evening, Night)
- **Weekend Trip**: Toggle switch

## API Integration

The API integration module (`js/api.js`) is fully implemented. It expects:

**Request:**
```json
POST /predict
{
  "route_id": 3,
  "weather": "cloudy",
  "passenger_count": 120,
  "time_of_day": 1,
  "is_weekend": 0
}
```

**Response:**
```json
{
  "predicted_delay": 18.5,
  "model_name": "Random Forest Regressor",
  "mae": 3.2
}
```

### Configuring API URL

By default, the app connects to `http://localhost:5000`. To change this:

1. **Option 1:** Set before the scripts load in `index.html`:
   ```html
   <script>window.API_BASE_URL = 'http://your-api-url:5000';</script>
   ```

2. **Option 2:** The app will fall back to mock mode if the API is unavailable (for testing UI without backend)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Design System

### Colors
- Primary: `#2563eb`
- Success: `#10b981`
- Error: `#ef4444`
- Background: `#f8fafc`

### Typography
- Font: Inter (system fallback)
- Base size: 16px
- Monospace: Courier New (for numeric outputs)

### Spacing
- Base unit: 4px
- Scale: xs, sm, md, lg, xl, 2xl, 3xl

## License

Academic Project | AI Coursework 2024

