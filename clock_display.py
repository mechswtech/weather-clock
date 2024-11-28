# Python script to display the weather and clock, running on raspberry pi

import requests
from tkinter import Tk, Label
from datetime import datetime, timedelta

# API URLs
CURRENT_WEATHER_API_URL = "http://IP_OF_ARDUINO"
ASTRONOMY_API_URL = "https://api.ipgeolocation.io/astronomy?apiKey=YOUR_KEY&lat=YOUR_LAT&long=YOUR_LONG"
FORECAST_API_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/59210?apikey=YOUR_KEY&metric=true"

# Global variables to store astronomy and forecast data
astronomy_data = {
    "sunrise": "N/A",
    "sunset": "N/A",
    "moonrise": "N/A",
    "moonset": "N/A",
    "last_updated": None
}

forecast_data = {
    "min_temp": "N/A",
    "max_temp": "N/A",
    "icon_phrase": "N/A",
    "last_updated": None
}


def fetch_current_weather_data():
    try:
        response = requests.get(CURRENT_WEATHER_API_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        temperature = data["temperature"]
        humidity = data["humidity"]
        return temperature, humidity
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Error fetching current weather data: {e}")
        return None, None

def fetch_astronomy_data():
    """Fetch astronomy data from IPGeolocation API and update global variables."""
    global astronomy_data
    response = requests.get(ASTRONOMY_API_URL)
    if response.status_code == 200:
        data = response.json()
        astronomy_data["sunrise"] = data.get("sunrise", "N/A")
        astronomy_data["sunset"] = data.get("sunset", "N/A")
        astronomy_data["moonrise"] = data.get("moonrise", "N/A")
        astronomy_data["moonset"] = data.get("moonset", "N/A")
        astronomy_data["last_updated"] = datetime.now()
    else:
        print(f"Astronomy API Error: {response.status_code}")

def get_astronomy_data():
    """Check if astronomy data needs to be updated and return current data."""
    global astronomy_data
    now = datetime.now()
    # Update data only if it hasn't been updated in the last hour
    if astronomy_data["last_updated"] is None or now - astronomy_data["last_updated"] > timedelta(hours=12):
        fetch_astronomy_data()
    return (
        astronomy_data["sunrise"],
        astronomy_data["sunset"],
        astronomy_data["moonrise"],
        astronomy_data["moonset"]
    )

def fetch_forecast_data():
    """Fetch forecast data from the API and update global variables."""
    global forecast_data
    response = requests.get(FORECAST_API_URL)
    if response.status_code == 200:
        data = response.json()
        daily_forecast = data["DailyForecasts"][0]
        forecast_data["min_temp"] = daily_forecast["Temperature"]["Minimum"]["Value"]
        forecast_data["max_temp"] = daily_forecast["Temperature"]["Maximum"]["Value"]
        forecast_data["icon_phrase"] = daily_forecast["Day"]["IconPhrase"]
        forecast_data["last_updated"] = datetime.now()
    else:
        print(f"Forecast API Error: {response.status_code}")

def get_forecast_data():
    """Check if forecast data needs to be updated and return current data."""
    global forecast_data
    now = datetime.now()
    # Update data only if it hasn't been updated in the last hour
    if forecast_data["last_updated"] is None or now - forecast_data["last_updated"] > timedelta(hours=12):
        fetch_forecast_data()
    return (
        forecast_data["min_temp"],
        forecast_data["max_temp"],
        forecast_data["icon_phrase"]
    )

def update_time():
    """Update the current time display every second."""
    current_time = datetime.now()
    time_label.config(text=current_time.strftime("%H:%M"))  # Display time in HH:MM format
    date_label.config(text=current_time.strftime("%d/%m %A"))  # Display date with weekday
    root.after(1000, update_time)  # Refresh every second


def update_data():
    """Update weather, astronomy, and forecast data every minute."""
    # Fetch current weather data
    temperature, humidity = fetch_current_weather_data()
    if temperature is not None and humidity is not None:
        outdoor_label.config(text=f"{temperature}°C {humidity}%")
    else:
        outdoor_label.config(text="Error fetching data")

    # Fetch astronomy data
    sunrise, sunset, moonrise, moonset = get_astronomy_data()
    sun_label.config(text=f"Sun: {sunrise} ~ {sunset}")
    moon_label.config(text=f"Moon: {moonrise} ~ {moonset}")

    # Fetch forecast data
    min_temp, max_temp, icon_phrase = get_forecast_data()
    forecast_label.config(text=f"Tomorrow: {min_temp}°C - {max_temp}°C ({icon_phrase})")

    # Refresh every 60 seconds
    root.after(60000, update_data)

# Main GUI Window
root = Tk()
root.title("Smart Clock")
root.attributes('-fullscreen', True)
root.configure(bg="#061f02")
root.config(cursor="none")

# Exit full screen with 'Esc' key
def exit_fullscreen(event):
    root.attributes('-fullscreen', False)

root.bind('<Escape>', exit_fullscreen)

# Widgets
date_label = Label(root, font=("Helvetica", 36), fg="white", bg="#061f02")  # Date at the top
date_label.pack(pady=10)

time_label = Label(root, font=("Helvetica", 110), fg="white", bg="#061f02")  # Time
time_label.pack(pady=10)

outdoor_label = Label(root, font=("Helvetica", 80), fg="white", bg="#061f02")  # Temperature & Humidity
outdoor_label.pack()

sun_label = Label(root, font=("Helvetica", 24), fg="white", bg="#061f02")  # Sunrise & Sunset
sun_label.pack(pady=10)

moon_label = Label(root, font=("Helvetica", 24), fg="white", bg="#061f02")  # Moonrise & Moonset
moon_label.pack(pady=10)

forecast_label = Label(root, font=("Helvetica", 24), fg="cyan", bg="#061f02")  # Tomorrow's Forecast
forecast_label.pack(pady=10)

# Start the display updates
update_time()  # Update time every second
update_data()  # Update weather, astronomy, and forecast data every minute

root.mainloop()
