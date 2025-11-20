// ============================================================================
// GLOBAL STATE
// ============================================================================
let currentLocation = null;

// ============================================================================
// INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    // Set max date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').max = today;
    document.getElementById('endDate').max = today;
    document.getElementById('editStartDate').max = today;
    document.getElementById('editEndDate').max = today;
    
    // Load saved records
    loadRecords();
});

// ============================================================================
// WEATHER SEARCH FUNCTIONS
// ============================================================================

// Handle Enter key in search
function handleSearchKeyPress(event) {
    if (event.key === 'Enter') {
        searchWeather();
    }
}

// Main weather search function
async function searchWeather() {
    const location = document.getElementById('searchLocation').value.trim();
    const errorEl = document.getElementById('searchError');
    
    // Clear errors
    errorEl.style.display = 'none';
    errorEl.textContent = '';
    
    // Validate input
    if (!location) {
        showError(errorEl, 'Please enter a location');
        return;
    }
    
    // Show loading state
    hideAllWeatherCards();
    showLoading('Fetching weather data...');
    
    try {
        const response = await fetch('/api/weather/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch weather');
        }
        
        const data = await response.json();
        currentLocation = data.location;
        
        // Display all weather information
        displayCurrentWeather(data.current, data.location);
        displayForecast(data.forecast);
        displayMap(data.location);
        
        if (data.videos && data.videos.length > 0) {
            displayVideos(data.videos);
        }
        
    } catch (error) {
        console.error('Search error:', error);
        showError(errorEl, error.message || 'Failed to fetch weather data. Please try again.');
    }
}

// Use current GPS location
function useCurrentLocation() {
    const errorEl = document.getElementById('searchError');
    errorEl.style.display = 'none';
    
    if (!navigator.geolocation) {
        showError(errorEl, 'Geolocation is not supported by your browser');
        return;
    }
    
    showLoading('Getting your location...');
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude.toFixed(4);
            const lon = position.coords.longitude.toFixed(4);
            document.getElementById('searchLocation').value = `${lat},${lon}`;
            searchWeather();
        },
        (error) => {
            hideLoading();
            showError(errorEl, 'Unable to get your location. Please enable location services.');
        }
    );
}

// ============================================================================
// DISPLAY FUNCTIONS
// ============================================================================

// Display current weather
function displayCurrentWeather(weather, location) {
    const card = document.getElementById('currentWeatherCard');
    const content = document.getElementById('currentWeatherContent');
    
    const iconUrl = `https://openweathermap.org/img/wn/${weather.weather[0].icon}@4x.png`;
    
    content.innerHTML = `
        <div class="weather-main">
            <div class="weather-info">
                <h3>${location.name}</h3>
                <div class="weather-temp">${Math.round(weather.main.temp)}°C</div>
                <div class="weather-desc">${weather.weather[0].description}</div>
            </div>
            <img src="${iconUrl}" alt="${weather.weather[0].description}" class="weather-icon">
        </div>
        
        <div class="weather-details">
            <div class="weather-detail">
                <i class="fas fa-temperature-high"></i>
                <div class="label">Feels Like</div>
                <div class="value">${Math.round(weather.main.feels_like)}°C</div>
            </div>
            <div class="weather-detail">
                <i class="fas fa-droplet"></i>
                <div class="label">Humidity</div>
                <div class="value">${weather.main.humidity}%</div>
            </div>
            <div class="weather-detail">
                <i class="fas fa-wind"></i>
                <div class="label">Wind Speed</div>
                <div class="value">${weather.wind.speed} m/s</div>
            </div>
            <div class="weather-detail">
                <i class="fas fa-gauge"></i>
                <div class="label">Pressure</div>
                <div class="value">${weather.main.pressure} hPa</div>
            </div>
            <div class="weather-detail">
                <i class="fas fa-eye"></i>
                <div class="label">Visibility</div>
                <div class="value">${(weather.visibility / 1000).toFixed(1)} km</div>
            </div>
            <div class="weather-detail">
                <i class="fas fa-cloud"></i>
                <div class="label">Cloudiness</div>
                <div class="value">${weather.clouds.all}%</div>
            </div>
        </div>
    `;
    
    card.style.display = 'block';
}

// Display 5-day forecast
function displayForecast(forecastData) {
    const card = document.getElementById('forecastCard');
    const content = document.getElementById('forecastContent');
    
    if (!forecastData || !forecastData.list) {
        return;
    }
    
    // Get one forecast per day (at noon)
    const dailyForecasts = [];
    const seenDates = new Set();
    
    forecastData.list.forEach(item => {
        const date = new Date(item.dt * 1000);
        const dateStr = date.toDateString();
        
        if (!seenDates.has(dateStr) && dailyForecasts.length < 5) {
            seenDates.add(dateStr);
            dailyForecasts.push(item);
        }
    });
    
    content.innerHTML = dailyForecasts.map(day => {
        const date = new Date(day.dt * 1000);
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const iconUrl = `https://openweathermap.org/img/wn/${day.weather[0].icon}@2x.png`;
        
        return `
            <div class="forecast-item">
                <div class="forecast-day">${dayName}, ${dateStr}</div>
                <img src="${iconUrl}" alt="${day.weather[0].description}" class="forecast-icon">
                <div class="forecast-temp">${Math.round(day.main.temp)}°C</div>
                <div class="forecast-desc">${day.weather[0].description}</div>
            </div>
        `;
    }).join('');
    
    card.style.display = 'block';
}

// Display Google Maps
function displayMap(location) {
    const card = document.getElementById('mapCard');
    const content = document.getElementById('mapContent');
    
    const mapUrl = `https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${location.lat},${location.lon}&zoom=10`;
    
    content.innerHTML = `<iframe src="${mapUrl}" allowfullscreen loading="lazy"></iframe>`;
    card.style.display = 'block';
}

// Display YouTube videos
function displayVideos(videos) {
    const card = document.getElementById('videosCard');
    const content = document.getElementById('videosContent');
    
    if (!videos || videos.length === 0) {
        return;
    }
    
    content.innerHTML = videos.map(video => `
        <div class="video-item">
            <iframe 
                src="https://www.youtube.com/embed/${video.videoId}"
                allowfullscreen
                loading="lazy"
            ></iframe>
            <div class="video-title">${video.title}</div>
        </div>
    `).join('');
    
    card.style.display = 'block';
}

// ============================================================================
// CRUD OPERATIONS
// ============================================================================

// CREATE - Save weather record
async function saveWeatherRecord() {
    const location = document.getElementById('saveLocation').value.trim();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const errorEl = document.getElementById('saveError');
    
    // Clear errors
    errorEl.style.display = 'none';
    
    // Validate
    if (!location || !startDate || !endDate) {
        showError(errorEl, 'Please fill in all fields');
        return;
    }
    
    // Show loading
    const recordsList = document.getElementById('recordsList');
    recordsList.innerHTML = '<div class="loading-message">Saving record...</div>';
    
    try {
        const response = await fetch('/api/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                location: location,
                start_date: startDate,
                end_date: endDate
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save record');
        }
        
        // Clear form
        document.getElementById('saveLocation').value = '';
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        
        // Reload records
        loadRecords();
        
    } catch (error) {
        console.error('Save error:', error);
        showError(errorEl, error.message);
        loadRecords();
    }
}

// READ - Load all records
async function loadRecords() {
    const container = document.getElementById('recordsList');
    container.innerHTML = '<div class="loading-message">Loading records...</div>';
    
    try {
        const response = await fetch('/api/records');
        
        if (!response.ok) {
            throw new Error('Failed to load records');
        }
        
        const records = await response.json();
        
        if (records.length === 0) {
            container.innerHTML = `
                <div class="empty-message">
                    <i class="fas fa-inbox"></i>
                    <p>No saved records yet.</p>
                    <p style="font-size: 13px; margin-top: 10px;">Save your first weather record above!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = records.map(record => createRecordHTML(record)).join('');
        
    } catch (error) {
        console.error('Load error:', error);
        container.innerHTML = '<div class="error-message">Failed to load records. Please refresh the page.</div>';
    }
}

// Create HTML for single record
function createRecordHTML(record) {
    const weatherTable = record.weather_data && record.weather_data.length > 0 ?
        createWeatherTable(record.weather_data) :
        '<p style="color: #999; font-size: 13px; font-style: italic;">No weather data available</p>';
    
    return `
        <div class="record-item">
            <div class="record-header">
                <div class="record-title">
                    <h4><i class="fas fa-map-marker-alt"></i> ${record.location_name}</h4>
                    <div class="record-meta">
                        <i class="far fa-calendar"></i> ${record.start_date} to ${record.end_date}
                        <br>
                        <i class="far fa-clock"></i> Saved: ${formatDateTime(record.created_at)}
                    </div>
                </div>
                <div class="record-actions">
                    <button onclick="editRecord(${record.id})" class="btn btn-primary btn-small">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteRecord(${record.id})" class="btn btn-danger btn-small">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button onclick="exportRecord(${record.id}, 'json')" class="btn btn-secondary btn-small" title="Export JSON">
                        <i class="fas fa-download"></i> JSON
                    </button>
                    <button onclick="exportRecord(${record.id}, 'csv')" class="btn btn-secondary btn-small" title="Export CSV">
                        <i class="fas fa-file-csv"></i> CSV
                    </button>
                </div>
            </div>
            ${weatherTable}
        </div>
    `;
}

// Create weather data table
function createWeatherTable(weatherData) {
    return `
        <table class="weather-data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Temperature</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Humidity</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                ${weatherData.map(day => `
                    <tr>
                        <td>${day.date}</td>
                        <td><strong>${day.temp}°C</strong></td>
                        <td>${day.temp_min}°C</td>
                        <td>${day.temp_max}°C</td>
                        <td>${day.humidity}%</td>
                        <td style="text-transform: capitalize;">${day.description}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// UPDATE - Edit record
async function editRecord(id) {
    try {
        const response = await fetch(`/api/records/${id}`);
        
        if (!response.ok) {
            throw new Error('Failed to load record');
        }
        
        const record = await response.json();
        
        // Populate modal
        document.getElementById('editRecordId').value = id;
        document.getElementById('editLocation').value = record.location_query;
        document.getElementById('editStartDate').value = record.start_date;
        document.getElementById('editEndDate').value = record.end_date;
        
        // Clear errors
        const errorEl = document.getElementById('editError');
        errorEl.style.display = 'none';
        
        // Show modal
        document.getElementById('editModal').style.display = 'flex';
        
    } catch (error) {
        console.error('Edit error:', error);
        alert('Failed to load record for editing');
    }
}

// Update record
async function updateRecord() {
    const id = document.getElementById('editRecordId').value;
    const location = document.getElementById('editLocation').value.trim();
    const startDate = document.getElementById('editStartDate').value;
    const endDate = document.getElementById('editEndDate').value;
    const errorEl = document.getElementById('editError');
    
    // Clear errors
    errorEl.style.display = 'none';
    
    // Validate
    if (!location || !startDate || !endDate) {
        showError(errorEl, 'Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`/api/records/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                location: location,
                start_date: startDate,
                end_date: endDate
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update record');
        }
        
        // Close modal and reload
        closeEditModal();
        loadRecords();
        
    } catch (error) {
        console.error('Update error:', error);
        showError(errorEl, error.message);
    }
}

// DELETE - Delete record
async function deleteRecord(id) {
    if (!confirm('Are you sure you want to delete this record?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/records/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete record');
        }
        
        loadRecords();
        
    } catch (error) {
        console.error('Delete error:', error);
        alert('Failed to delete record');
    }
}

// EXPORT - Export record
async function exportRecord(id, format) {
    try {
        const response = await fetch(`/api/records/${id}/export/${format}`);
        
        if (!response.ok) {
            throw new Error('Failed to export record');
        }
        
        if (format === 'json') {
            const data = await response.json();
            downloadJSON(data, `weather_record_${id}.json`);
        } else if (format === 'csv') {
            const blob = await response.blob();
            downloadBlob(blob, `weather_record_${id}.csv`);
        }
        
    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export record');
    }
}

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target === modal) {
        closeEditModal();
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

function showLoading(message) {
    // Could show a loading overlay if desired
    console.log(message);
}

function hideLoading() {
    // Hide loading overlay
}

function hideAllWeatherCards() {
    document.getElementById('currentWeatherCard').style.display = 'none';
    document.getElementById('forecastCard').style.display = 'none';
    document.getElementById('mapCard').style.display = 'none';
    document.getElementById('videosCard').style.display = 'none';
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function downloadJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    downloadBlob(blob, filename);
}

function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}