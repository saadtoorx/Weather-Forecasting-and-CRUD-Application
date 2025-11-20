# 🌤️ Advanced Weather Application

A comprehensive weather tracking application with real-time weather data, forecasts, CRUD operations, and additional API integrations.

## ✨ Features Overview

### Task 1: Basic Weather App ✅
- ✅ **Multiple Location Inputs**: City names, zip codes, GPS coordinates, landmarks
- ✅ **Current Weather Display**: Temperature, humidity, wind speed, pressure, visibility
- ✅ **5-Day Forecast**: Detailed weather predictions
- ✅ **GPS Location**: Automatic location detection
- ✅ **Weather Icons**: Visual weather representations
- ✅ **Real-Time API Data**: OpenWeatherMap integration

### Task 2: Advanced Features ✅
- ✅ **Full CRUD Operations**: Create, Read, Update, Delete weather records
- ✅ **Database Persistence**: SQLite database storage
- ✅ **Date Range Validation**: Prevents invalid date inputs
- ✅ **Location Validation**: Fuzzy matching for location names
- ✅ **Data Export**: JSON and CSV formats
- ✅ **Google Maps Integration**: Visual location display
- ✅ **YouTube Videos**: Travel videos for locations (optional)

## 🛠️ Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **API**: OpenWeatherMap (current weather + forecast)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Additional APIs**: YouTube Data API (optional), Google Maps Embed API

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **pip** package manager
3. **OpenWeatherMap API Key** (free tier available)
4. **YouTube API Key** (optional, for video feature)

## 🚀 Installation & Setup

### Step 1: Get API Keys

**OpenWeatherMap (Required):**
1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Go to API Keys section
4. Copy your API key

**YouTube Data API (Optional):**
1. Visit https://console.developers.google.com/
2. Create new project
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy your API key

### Step 2: Install Dependencies

```bash
# Clone or download the project
cd advanced-weather-app

# Install Python packages
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
OPENWEATHER_API_KEY=your_openweathermap_key_here
YOUTUBE_API_KEY=your_youtube_key_here
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start at: http://127.0.0.1:5000

## 📁 Project Structure

```
advanced-weather-app/
│
├── app.py                  # Flask backend with all API routes
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # Template for environment variables
├── weather_data.db        # SQLite database (auto-created)
│
├── templates/
│   └── index.html         # Main HTML page
│
└── static/
    ├── style.css          # Styling and responsive design
    └── script.js          # Frontend JavaScript logic
```

## 📖 How to Use

### 1. Search Current Weather

**Quick Search:**
1. Enter a location in the search box:
   - City name: `London`, `New York`, `Tokyo`
   - Zip code: `10001`, `90210`
   - Coordinates: `40.7128,-74.0060`
2. Click "Search" or press Enter
3. View current weather, 5-day forecast, map, and videos

**GPS Location:**
1. Click "My Location" button
2. Allow location permission
3. Automatically fetch weather for your location

### 2. Save Weather Records (CRUD Operations)

**CREATE - Save New Record:**
1. In the right panel, enter:
   - Location (city, zip, or coordinates)
   - Start date (cannot be in future)
   - End date (cannot be in future)
2. Click "Save Record"
3. Record appears in "Saved Weather Records" below

**READ - View Records:**
- All saved records appear in the right panel
- Shows location, date range, and weather data table
- Automatically loads on page refresh

**UPDATE - Edit Record:**
1. Click the edit button (✏️) on any record
2. Modify location or date range
3. Click "Update" in the modal
4. Weather data is refreshed automatically

**DELETE - Remove Record:**
1. Click the delete button (🗑️) on any record
2. Confirm deletion
3. Record is permanently removed

**EXPORT - Download Data:**
- Click "JSON" button to download JSON format
- Click "CSV" button to download CSV spreadsheet
- Files download automatically to your computer

### 3. Additional Features

**Google Maps:**
- Automatically displays when you search for a location
- Shows the location on an interactive map
- Can zoom and navigate

**YouTube Videos:**
- Shows travel videos related to the location
- Only appears if YouTube API key is configured
- Displays 3 relevant videos

## 🎯 API Endpoints

### Weather Search
```
POST /api/weather/search
Body: { "location": "London" }
Returns: Current weather, forecast, location data, videos
```

### CRUD Operations

**Create Record:**
```
POST /api/records
Body: {
  "location": "London",
  "start_date": "2024-11-01",
  "end_date": "2024-11-10"
}
```

**Read All Records:**
```
GET /api/records
Returns: Array of all saved records
```

**Read Single Record:**
```
GET /api/records/{id}
Returns: Single record with all data
```

**Update Record:**
```
PUT /api/records/{id}
Body: {
  "location": "Paris",
  "start_date": "2024-11-01",
  "end_date": "2024-11-05"
}
```

**Delete Record:**
```
DELETE /api/records/{id}
Returns: Success confirmation
```

**Export Record:**
```
GET /api/records/{id}/export/json
GET /api/records/{id}/export/csv
Returns: Downloadable file
```

## 🔧 Configuration

### Database
- **Type**: SQLite
- **File**: `weather_data.db`
- **Auto-created** on first run
- **Location**: Project root directory

### API Rate Limits
- **OpenWeatherMap Free Tier**:
  - 1,000 calls/day
  - 60 calls/minute
  
- **YouTube Data API Free Tier**:
  - 10,000 units/day
  - Each search = 100 units

## 🎨 UI/UX Features

### Responsive Design
- Works on desktop, tablet, and mobile
- Grid layout automatically adjusts
- Touch-friendly buttons

### Visual Feedback
- Loading states during API calls
- Error messages with helpful hints
- Success confirmations
- Hover effects on interactive elements

### Color Scheme
- Primary: Purple gradient (`#667eea` to `#764ba2`)
- Accents: Various button colors
- Clean white cards with shadows

## 🐛 Troubleshooting

### "Missing API Key" Error
**Solution:**
- Ensure `.env` file exists in project root
- Check API key is correct (no quotes, no spaces)
- Verify API key format: `OPENWEATHER_API_KEY=abc123xyz`

### "Location Not Found" Error
**Solution:**
- Try different search terms
- Use coordinates for precise locations
- Check spelling of city names
- Try format: "City, Country" (e.g., "Paris, France")

### Date Validation Errors
**Solution:**
- Ensure start date is before end date
- Both dates must be in the past or today
- Date range cannot exceed 30 days
- Use format: YYYY-MM-DD

### Database Errors
**Solution:**
```bash
# Delete database and restart
rm weather_data.db
python app.py
```

### No YouTube Videos Appearing
**Cause:** YouTube API key not configured
**Solution:** This is optional - app works without it

## 📊 Database Schema

**WeatherRecord Table:**
```sql
id              INTEGER PRIMARY KEY
location_name   VARCHAR(200)    # Full location name
location_query  VARCHAR(200)    # Original search query
latitude        FLOAT           # Latitude coordinate
longitude       FLOAT           # Longitude coordinate
start_date      VARCHAR(10)     # Start date (YYYY-MM-DD)
end_date        VARCHAR(10)     # End date (YYYY-MM-DD)
weather_data    TEXT            # JSON string of weather data
created_at      DATETIME        # When record was created
updated_at      DATETIME        # When record was updated
```

## 🔐 Security Notes

### API Key Protection
- ✅ API keys stored in `.env` file
- ✅ `.env` excluded from version control
- ✅ Backend handles all API calls
- ✅ No API keys exposed to frontend

### Add to `.gitignore`:
```
.env
*.db
__pycache__/
*.pyc
*.pyo
```

## 🚀 Deployment Options

### Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Install gunicorn
pip install gunicorn

# Deploy
heroku create
git push heroku main
```

### PythonAnywhere
1. Upload files via Files tab
2. Set up virtual environment
3. Configure WSGI file
4. Add environment variables in Web tab

### Railway/Render
1. Connect GitHub repository
2. Add environment variables in dashboard
3. Deploy automatically

## 📈 Possible Enhancements

**Future Features:**
- User authentication and accounts
- Weather alerts and notifications
- Data visualization with charts
- Historical data comparison
- Weather predictions using ML
- Mobile app version
- Real-time weather updates
- Social sharing features

## 🧪 Testing Checklist

### Basic Features
- [ ] Search by city name
- [ ] Search by zip code
- [ ] Search by coordinates
- [ ] GPS location works
- [ ] Current weather displays
- [ ] 5-day forecast shows
- [ ] Maps display correctly

### CRUD Operations
- [ ] Can create new record
- [ ] Records appear in list
- [ ] Can edit existing record
- [ ] Can delete record
- [ ] Export JSON works
- [ ] Export CSV works

### Validation
- [ ] Empty location rejected
- [ ] Invalid dates rejected
- [ ] Future dates rejected
- [ ] Start date > end date rejected
- [ ] Date range > 30 days rejected

### Error Handling
- [ ] Invalid location shows error
- [ ] Network errors handled
- [ ] API errors handled gracefully

## 💡 Code Highlights for Interview

### Backend (app.py)
**Key Concepts:**
- RESTful API design
- SQLAlchemy ORM usage
- Error handling with try-catch
- Data validation functions
- External API integration
- CSV/JSON export functionality

### Frontend (script.js)
**Key Concepts:**
- Async/await for API calls
- DOM manipulation
- Event handling
- State management
- Error handling
- File download implementation

### Database Design
**Key Concepts:**
- Normalized schema
- Appropriate data types
- Timestamp tracking
- JSON storage for complex data

## 📝 Assessment Criteria Met

### Task 1 Requirements:
✅ Multiple location input methods
✅ Current weather display with useful details
✅ 5-day forecast
✅ GPS location support
✅ Weather icons and visual design
✅ Real API integration (no static data)

### Task 2 Requirements:
✅ **CREATE**: Save weather with date range + validation
✅ **READ**: View all saved records
✅ **UPDATE**: Edit records with validation
✅ **DELETE**: Remove records
✅ **Database**: SQLite with SQLAlchemy
✅ **Validation**: Date ranges and location existence
✅ **API Integration**: YouTube videos, Google Maps
✅ **Data Export**: JSON and CSV formats

### Code Quality:
✅ Beginner-friendly code
✅ Clear comments and documentation
✅ Clean code structure
✅ Error handling throughout
✅ Responsive UI design

## 👤 Author

Created for AI Engineer Internship Assessment

## 📄 License

This project is created as an assessment task.

---

## Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
echo "OPENWEATHER_API_KEY=your_key" > .env

# 3. Run application
python app.py

# 4. Open browser
# http://127.0.0.1:5000
```

**Good luck with your assessment! 🎯**