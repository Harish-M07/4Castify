from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from collections import defaultdict
import os
import requests
from .core.config import API_KEY

app = FastAPI()

# --- Helper Functions (No Changes) ---
def format_weather_data(data):
    wind_speed_kmh = round(data['wind']['speed'] * 3.6, 1)
    sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
    sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
    return { "locationName": f"{data['name']}, {data['sys']['country']}", "temperature": round(data['main']['temp']), "feelsLike": round(data['main']['feels_like']), "description": data['weather'][0]['description'], "icon": data['weather'][0]['icon'], "humidity": data['main']['humidity'], "windSpeed": wind_speed_kmh, "sunrise": sunrise_time, "sunset": sunset_time, }
def format_hourly_forecast_data(data):
    formatted_list = []
    for item in data['list'][:8]: formatted_list.append({ "time": datetime.fromtimestamp(item['dt']).strftime('%H:%M'), "temperature": round(item['main']['temp']), "icon": item['weather'][0]['icon'] })
    return formatted_list
def format_daily_forecast_data(data):
    daily_data = defaultdict(lambda: {'temps': [], 'icons': []})
    for item in data['list']:
        date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
        daily_data[date]['temps'].append(item['main']['temp'])
        if '12:00:00' in item['dt_txt']: daily_data[date]['icons'].insert(0, item['weather'][0]['icon'])
        else: daily_data[date]['icons'].append(item['weather'][0]['icon'])
    formatted_list = []
    for date_str, values in daily_data.items():
        if not values['temps']: continue
        day_of_week = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
        if day_of_week == datetime.now().strftime('%A'): continue
        formatted_list.append({ "day": day_of_week, "temp_max": round(max(values['temps'])), "temp_min": round(min(values['temps'])), "icon": values['icons'][0] if values['icons'] else '01d' })
    return formatted_list[:5]

# --- API Endpoints (No Changes) ---
@app.get("/api/weather")
def get_weather(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try: response = requests.get(url); response.raise_for_status(); return format_weather_data(response.json())
    except requests.exceptions.RequestException as e: raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
@app.get("/api/hourly_forecast")
def get_hourly_forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try: response = requests.get(url); response.raise_for_status(); return format_hourly_forecast_data(response.json())
    except requests.exceptions.RequestException as e: raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
@app.get("/api/daily_forecast")
def get_daily_forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try: response = requests.get(url); response.raise_for_status(); return format_daily_forecast_data(response.json())
    except requests.exceptions.RequestException as e: raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

# --- CORRECT CODE TO SERVE FRONTEND ---
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(current_dir), "frontend")

# Mount static files
app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

# Serve the index.html as the root
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))