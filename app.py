"""
Advanced Weather Application
Combines current weather, forecasts, CRUD operations, and API integrations
"""

import os
import json
from datetime import datetime, timedelta
import io
import csv

from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # Optional

if not OPENWEATHER_API_KEY:
    raise ValueError("❌ Missing OPENWEATHER_API_KEY in .env file")

# Flask setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather_data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ============================================================================
# DATABASE MODEL
# ============================================================================
class WeatherRecord(db.Model):
    """Model for storing weather records with CRUD operations."""
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(200), nullable=False)
    location_query = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    end_date = db.Column(db.String(10), nullable=False)
    weather_data = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "location_name": self.location_name,
            "location_query": self.location_query,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "weather_data": json.loads(self.weather_data) if self.weather_data else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

# ============================================================================
# HELPER FUNCTIONS - VALIDATION
# ============================================================================
def validate_date(date_str):
    """Validate date string in YYYY-MM-DD format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        if date_obj > today:
            return None, "Date cannot be in the future"
        return date_obj, None
    except ValueError:
        return None, "Invalid date format. Use YYYY-MM-DD"

def validate_date_range(start_date_str, end_date_str):
    """Validate date range."""
    start, error1 = validate_date(start_date_str)
    end, error2 = validate_date(end_date_str)
    
    if error1:
        return None, None, error1
    if error2:
        return None, None, error2
    if start > end:
        return None, None, "Start date must be before or equal to end date"
    
    # Check range is not too large (max 30 days for free tier)
    if (end - start).days > 30:
        return None, None, "Date range cannot exceed 30 days"
    
    return start, end, None

# ============================================================================
# HELPER FUNCTIONS - OPENWEATHERMAP API
# ============================================================================
def geocode_location(query):
    """
    Geocode location using OpenWeatherMap Geocoding API.
    Supports: city names, zip codes, coordinates.
    Returns: dict with name, lat, lon or None
    """
    # Check if input is coordinates (lat,lon)
    if "," in query:
        try:
            parts = query.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            # Reverse geocode to get location name
            return reverse_geocode(lat, lon)
        except:
            pass
    
    # Try direct geocoding
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": query,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not data:
            return None
        
        location = data[0]
        return {
            "name": f"{location['name']}, {location.get('state', '')}, {location['country']}".replace(", ,", ","),
            "lat": location["lat"],
            "lon": location["lon"]
        }
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def reverse_geocode(lat, lon):
    """Reverse geocode coordinates to location name."""
    url = "http://api.openweathermap.org/geo/1.0/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {"name": f"{lat}, {lon}", "lat": lat, "lon": lon}
        
        data = response.json()
        if not data:
            return {"name": f"{lat}, {lon}", "lat": lat, "lon": lon}
        
        location = data[0]
        return {
            "name": f"{location['name']}, {location.get('state', '')}, {location['country']}".replace(", ,", ","),
            "lat": lat,
            "lon": lon
        }
    except:
        return {"name": f"{lat}, {lon}", "lat": lat, "lon": lon}

def get_current_weather(lat, lon):
    """Get current weather for coordinates."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        print(f"Current weather error: {e}")
        return None

def get_forecast(lat, lon):
    """Get 5-day forecast for coordinates."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        print(f"Forecast error: {e}")
        return None

def get_historical_weather(lat, lon, start_date, end_date):
    """
    Get historical weather data for date range.
    Note: OpenWeatherMap free tier doesn't support historical data.
    This simulates historical data using current weather.
    For production, use a paid plan or different API.
    """
    # For demonstration, we'll use forecast data
    forecast_data = get_forecast(lat, lon)
    if not forecast_data:
        return []
    
    results = []
    for item in forecast_data.get("list", [])[:8]:  # First 8 entries (24 hours)
        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
        results.append({
            "date": date,
            "temp": round(item["main"]["temp"], 1),
            "temp_min": round(item["main"]["temp_min"], 1),
            "temp_max": round(item["main"]["temp_max"], 1),
            "feels_like": round(item["main"]["feels_like"], 1),
            "humidity": item["main"]["humidity"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"]
        })
    
    return results

# ============================================================================
# HELPER FUNCTIONS - ADDITIONAL APIs (OPTIONAL)
# ============================================================================
def get_youtube_videos(location_name):
    """Get YouTube videos for a location (optional)."""
    if not YOUTUBE_API_KEY:
        return []
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{location_name} travel guide",
        "key": YOUTUBE_API_KEY,
        "maxResults": 3,
        "type": "video"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return []
        
        data = response.json()
        videos = []
        for item in data.get("items", []):
            videos.append({
                "title": item["snippet"]["title"],
                "videoId": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
            })
        return videos
    except Exception as e:
        print(f"YouTube API error: {e}")
        return []

# ============================================================================
# ROUTES - MAIN PAGE
# ============================================================================
@app.route("/")
def index():
    """Render main page."""
    return render_template("index.html")

# ============================================================================
# ROUTES - WEATHER SEARCH
# ============================================================================
@app.route("/api/weather/search", methods=["POST"])
def search_weather():
    """Search for current weather and forecast."""
    try:
        data = request.get_json()
        location_query = data.get("location", "").strip()
        
        if not location_query:
            return jsonify({"error": "Location is required"}), 400
        
        # Geocode location
        location = geocode_location(location_query)
        if not location:
            return jsonify({"error": "Location not found"}), 404
        
        # Get current weather
        current = get_current_weather(location["lat"], location["lon"])
        if not current:
            return jsonify({"error": "Failed to fetch weather data"}), 500
        
        # Get forecast
        forecast = get_forecast(location["lat"], location["lon"])
        
        # Get YouTube videos (optional)
        videos = get_youtube_videos(location["name"])
        
        return jsonify({
            "location": location,
            "current": current,
            "forecast": forecast,
            "videos": videos
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# ROUTES - CRUD OPERATIONS
# ============================================================================

# CREATE
@app.route("/api/records", methods=["POST"])
def create_record():
    """Create new weather record with date range."""
    try:
        data = request.get_json()
        
        location_query = data.get("location", "").strip()
        start_date_str = data.get("start_date", "").strip()
        end_date_str = data.get("end_date", "").strip()
        
        # Validation
        if not location_query:
            return jsonify({"error": "Location is required"}), 400
        if not start_date_str or not end_date_str:
            return jsonify({"error": "Date range is required"}), 400
        
        # Validate dates
        start_date, end_date, error = validate_date_range(start_date_str, end_date_str)
        if error:
            return jsonify({"error": error}), 400
        
        # Geocode location
        location = geocode_location(location_query)
        if not location:
            return jsonify({"error": "Location not found. Please check spelling or try coordinates."}), 404
        
        # Get weather data for date range
        weather_data = get_historical_weather(
            location["lat"],
            location["lon"],
            start_date,
            end_date
        )
        
        # Create record
        record = WeatherRecord(
            location_name=location["name"],
            location_query=location_query,
            latitude=location["lat"],
            longitude=location["lon"],
            start_date=start_date_str,
            end_date=end_date_str,
            weather_data=json.dumps(weather_data)
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "record": record.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Create error: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to create record"}), 500

# READ - All records
@app.route("/api/records", methods=["GET"])
def get_all_records():
    """Get all weather records."""
    try:
        records = WeatherRecord.query.order_by(WeatherRecord.created_at.desc()).all()
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        print(f"Read error: {e}")
        return jsonify({"error": "Failed to fetch records"}), 500

# READ - Single record
@app.route("/api/records/<int:record_id>", methods=["GET"])
def get_record(record_id):
    """Get single weather record."""
    try:
        record = WeatherRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Record not found"}), 404
        return jsonify(record.to_dict())
    except Exception as e:
        print(f"Read error: {e}")
        return jsonify({"error": "Failed to fetch record"}), 500

# UPDATE
@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    """Update weather record."""
    try:
        record = WeatherRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Record not found"}), 404
        
        data = request.get_json()
        
        # Get updated values
        location_query = data.get("location", record.location_query).strip()
        start_date_str = data.get("start_date", record.start_date).strip()
        end_date_str = data.get("end_date", record.end_date).strip()
        
        # Validate dates
        start_date, end_date, error = validate_date_range(start_date_str, end_date_str)
        if error:
            return jsonify({"error": error}), 400
        
        # Geocode location if changed
        if location_query != record.location_query:
            location = geocode_location(location_query)
            if not location:
                return jsonify({"error": "Location not found"}), 404
            
            record.location_name = location["name"]
            record.location_query = location_query
            record.latitude = location["lat"]
            record.longitude = location["lon"]
        
        # Update dates
        record.start_date = start_date_str
        record.end_date = end_date_str
        
        # Refresh weather data
        weather_data = get_historical_weather(
            record.latitude,
            record.longitude,
            start_date,
            end_date
        )
        record.weather_data = json.dumps(weather_data)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "record": record.to_dict()
        })
        
    except Exception as e:
        print(f"Update error: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to update record"}), 500

# DELETE
@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    """Delete weather record."""
    try:
        record = WeatherRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Record not found"}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Delete error: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to delete record"}), 500

# ============================================================================
# ROUTES - DATA EXPORT
# ============================================================================
@app.route("/api/records/<int:record_id>/export/<format>", methods=["GET"])
def export_record(record_id, format):
    """Export record in various formats: json, csv."""
    try:
        record = WeatherRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Record not found"}), 404
        
        data = record.to_dict()
        
        # JSON Export
        if format == "json":
            return jsonify(data)
        
        # CSV Export
        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow([
                "Record ID", "Location", "Latitude", "Longitude",
                "Start Date", "End Date", "Date", "Temperature",
                "Min Temp", "Max Temp", "Humidity", "Description"
            ])
            
            # Data rows
            weather_data = data.get("weather_data", [])
            for item in weather_data:
                writer.writerow([
                    data["id"],
                    data["location_name"],
                    data["latitude"],
                    data["longitude"],
                    data["start_date"],
                    data["end_date"],
                    item.get("date", ""),
                    item.get("temp", ""),
                    item.get("temp_min", ""),
                    item.get("temp_max", ""),
                    item.get("humidity", ""),
                    item.get("description", "")
                ])
            
            response = make_response(output.getvalue())
            response.headers["Content-Type"] = "text/csv"
            response.headers["Content-Disposition"] = f"attachment; filename=weather_{record_id}.csv"
            return response
        
        else:
            return jsonify({"error": "Unsupported format"}), 400
            
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({"error": "Failed to export record"}), 500

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌤️  ADVANCED WEATHER APPLICATION")
    print("="*60)
    print(f"✅ OpenWeatherMap API Key: {'Loaded' if OPENWEATHER_API_KEY else 'Missing'}")
    print(f"💡 YouTube API Key: {'Loaded' if YOUTUBE_API_KEY else 'Not configured (optional)'}")
    print("\n🚀 Starting server...")
    print("📍 Access at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True)