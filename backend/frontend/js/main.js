document.addEventListener('DOMContentLoaded', () => {
    const splashScreen = document.getElementById('splash-screen');
    const appContainer = document.getElementById('app-container');
    const errorCard = document.getElementById('error-card');
    const backendUrl = '';
    let hourlyChart = null;
    
    const setDynamicTheme = () => { /* ... (function is unchanged) ... */ };
    
    // NEW: Function to get and display the current date
    const updateDate = () => {
        const dateElement = document.getElementById('current-date');
        if (dateElement) {
            const now = new Date();
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            // Formats the date to be like "Friday, 3 October 2025"
            dateElement.textContent = now.toLocaleDateString('en-GB', options);
        }
    };

    const updateClock = () => { /* ... (function is unchanged) ... */ };

    // Run all the time/date functions on page load
    setDynamicTheme();
    updateDate(); // Run the new date function once
    updateClock();
    setInterval(updateClock, 1000);

    // ... (The rest of the file is exactly the same) ...
    const showApp = () => { if (splashScreen && appContainer) { splashScreen.classList.add('fade-out'); appContainer.classList.remove('hidden'); appContainer.classList.add('fade-in'); setTimeout(() => { splashScreen.style.display = 'none'; }, 500); } };
    const showError = (message) => { console.error("Displaying error:", message); if (splashScreen) splashScreen.style.display = 'none'; if (errorCard) { errorCard.querySelector('p').textContent = `Error: ${message}`; errorCard.classList.remove('hidden'); } };
    const displayCurrentWeather = (data) => { document.getElementById('location').textContent = data.locationName; document.getElementById('temperature').textContent = `${data.temperature}°C`; document.getElementById('description').textContent = data.description; document.getElementById('weather-icon').src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`; document.getElementById('feels-like').textContent = `${data.feelsLike}°C`; document.getElementById('humidity').textContent = `${data.humidity}%`; document.getElementById('wind').textContent = `${data.windSpeed} km/h`; document.getElementById('sunrise').textContent = data.sunrise; document.getElementById('sunset').textContent = data.sunset; };
    const displayHourlyForecast = (hourlyData) => { const container = document.getElementById('hourly-forecast-scroll'); container.innerHTML = ''; hourlyData.forEach(item => { const itemDiv = document.createElement('div'); itemDiv.classList.add('hourly-item'); itemDiv.innerHTML = `<p class="time">${item.time}</p><img class="icon" src="https://openweathermap.org/img/wn/${item.icon}.png" alt="Weather icon"><p class="temp">${item.temperature}°</p>`; container.appendChild(itemDiv); }); };
    const displayHourlyChart = (hourlyData) => { const ctx = document.getElementById('hourly-chart').getContext('2d'); const labels = hourlyData.map(item => item.time); const temperatures = hourlyData.map(item => item.temperature); const isNightTheme = document.body.classList.contains('theme-night'); const chartColor = isNightTheme ? '#FFFFFF' : '#4A90E2'; const gridColor = isNightTheme ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)'; if (hourlyChart) { hourlyChart.destroy(); } hourlyChart = new Chart(ctx, { type: 'line', data: { labels: labels, datasets: [{ label: 'Temperature', data: temperatures, fill: true, borderColor: chartColor, backgroundColor: 'rgba(74, 144, 226, 0.1)', tension: 0.4, pointRadius: 0 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: false, ticks: { color: chartColor, callback: function(value) { return value + '°'; } }, grid: { color: gridColor } }, x: { grid: { display: false }, ticks: { color: chartColor } } } } }); };
    const displayDailyForecast = (dailyData) => { const container = document.getElementById('daily-forecast-list'); container.innerHTML = ''; dailyData.forEach(item => { const itemDiv = document.createElement('div'); itemDiv.classList.add('daily-item'); itemDiv.innerHTML = `<p class="day">${item.day}</p><img class="icon" src="https://openweathermap.org/img/wn/${item.icon}.png" alt="Weather icon"><p class="temps"><strong>${item.temp_max}°</strong> / <span>${item.temp_min}°</span></p>`; container.appendChild(itemDiv); }); };
    const fetchAllData = async (lat, lon) => { const weatherUrl = `${backendUrl}/api/weather?lat=${lat}&lon=${lon}`; const hourlyUrl = `${backendUrl}/api/hourly_forecast?lat=${lat}&lon=${lon}`; const dailyUrl = `${backendUrl}/api/daily_forecast?lat=${lat}&lon=${lon}`; try { const responses = await Promise.all([ fetch(weatherUrl), fetch(hourlyUrl), fetch(dailyUrl) ]); for (const response of responses) { if (!response.ok) { const errorData = await response.json(); throw new Error(errorData.detail || `API request failed with status: ${response.status}`); } } const [weatherData, hourlyData, dailyData] = await Promise.all(responses.map(res => res.json())); displayCurrentWeather(weatherData); displayHourlyForecast(hourlyData); displayHourlyChart(hourlyData); displayDailyForecast(dailyData); showApp(); } catch (error) { showError(error.message); } };
    const getLocation = () => { if (navigator.geolocation) { navigator.geolocation.getCurrentPosition((position) => { fetchAllData(position.coords.latitude, position.coords.longitude); }, (error) => { showError(error.message); }); } else { showError('Geolocation is not supported by this browser.'); } };
    
    getLocation();
});