from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from .core.config import API_KEY
from datetime import datetime
from collections import defaultdict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_weather_data(data):
    """Formats the raw CURRENT weather data."""
    wind_speed_kmh = round(data['wind']['speed'] * 3.6, 1)
    sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
    sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
    
    return {
        "locationName": f"{data['name']}, {data['sys']['country']}",
        "temperature": round(data['main']['temp']),
        "feelsLike": round(data['main']['feels_like']),
        "description": data['weather'][0]['description'],
        "icon": data['weather'][0]['icon'],
        "humidity": data['main']['humidity'],
        "windSpeed": wind_speed_kmh,
        "sunrise": sunrise_time,
        "sunset": sunset_time,
    }

def format_hourly_forecast_data(data):
    """Formats the raw HOURLY forecast data."""
    formatted_list = []
    for item in data['list'][:8]: # First 8 items for a 24-hour forecast
        formatted_list.append({
            "time": datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
            "temperature": round(item['main']['temp']),
            "icon": item['weather'][0]['icon']
        })
    return formatted_list

# NEW: Helper function to process 3-hour data into a daily summary
def format_daily_forecast_data(data):
    """Formats the raw forecast data into a 5-day summary."""
    daily_data = defaultdict(lambda: {'temps': [], 'icons': []})
    
    # Group temperatures and icons by day
    for item in data['list']:
        date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
        daily_data[date]['temps'].append(item['main']['temp'])
        # Give more weight to daytime icons (e.g., around noon)
        if '12:00:00' in item['dt_txt']:
            daily_data[date]['icons'].insert(0, item['weather'][0]['icon'])
        else:
            daily_data[date]['icons'].append(item['weather'][0]['icon'])

    formatted_list = []
    # Find min/max temps and the most common icon for each day
    for date_str, values in daily_data.items():
        if not values['temps']: continue
        
        day_of_week = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
        
        # Don't show today's forecast in the list if we only have a partial day
        if day_of_week == datetime.now().strftime('%A'):
            continue

        formatted_list.append({
            "day": day_of_week,
            "temp_max": round(max(values['temps'])),
            "temp_min": round(min(values['temps'])),
            "icon": values['icons'][0] if values['icons'] else '01d' # Default icon
        })

    return formatted_list[:5] # Return up to 5 days


@app.get("/")
def read_root(): return {"message": "Welcome"}

@app.get("/api/weather")
def get_weather(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return format_weather_data(response.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

@app.get("/api/hourly_forecast")
def get_hourly_forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return format_hourly_forecast_data(response.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

# NEW: Endpoint for the daily forecast
@app.get("/api/daily_forecast")
def get_daily_forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return format_daily_forecast_data(response.json())
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")