from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from collections import defaultdict
import os
import requests
from .core.config import API_KEY

# NEW: Import the CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# NEW: Add the CORS permission block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Helper Functions (No Changes) ---
def format_weather_data(data):
    # ... (code is the same)
    wind_speed_kmh = round(data['wind']['speed'] * 3.6, 1); sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'); sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'); return { "locationName": f"{data['name']}, {data['sys']['country']}", "temperature": round(data['main']['temp']), "feelsLike": round(data['main']['feels_like']), "description": data['weather'][0]['description'], "icon": data['weather'][0]['icon'], "humidity": data['main']['humidity'], "windSpeed": wind_speed_kmh, "sunrise": sunrise_time, "sunset": sunset_time, }
def format_hourly_forecast_data(data):
    # ... (code is the same)
    formatted_list = []; [formatted_list.append({ "time": datetime.fromtimestamp(item['dt']).strftime('%H:%M'), "temperature": round(item['main']['temp']), "icon": item['weather'][0]['icon'] }) for item in data['list'][:8]]; return formatted_list
def format_daily_forecast_data(data):
    # ... (code is the same)
    daily_data = defaultdict(lambda: {'temps': [], 'icons': []}); [ (daily_data[datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')]['temps'].append(item['main']['temp']), daily_data[datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')]['icons'].insert(0, item['weather'][0]['icon']) if '12:00:00' in item['dt_txt'] else daily_data[datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')]['icons'].append(item['weather'][0]['icon'])) for item in data['list'] ]; formatted_list = []; [ formatted_list.append({ "day": datetime.strptime(date_str, '%Y-%m-%d').strftime('%A'), "temp_max": round(max(values['temps'])), "temp_min": round(min(values['temps'])), "icon": values['icons'][0] if values['icons'] else '01d' }) for date_str, values in daily_data.items() if values['temps'] and datetime.strptime(date_str, '%Y-%m-%d').strftime('%A') != datetime.now().strftime('%A') ]; return formatted_list[:5]

# --- API Endpoints (No Changes) ---
@app.get("/api/weather")
def get_weather(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric";
    try: response = requests.get(url); response.raise_for_status(); return format_weather_data(response.json())
    except requests.exceptions.RequestException as e: raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
@app.get("/api/hourly_forecast")
def get_hourly_forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric";
    try: response = requests.get(url); response.raise_for_status(); return format_hourly_forecast_data(response.json())
    except requests.exceptions.RequestException as e: raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
@app.get("/api/daily_forecast")
def get_daily_forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric";
    try: response = requests.get(url); response.raise_for_status(); return format_daily_forecast_data(response.json())
    except requests.exceptions.RequestException as e: raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

# --- Code to Serve Frontend (No Changes) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(current_dir), "frontend")
app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
app.mount("/img", StaticFiles(directory=os.path.join(frontend_dir, "img")), name="img")
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))