# Python script to display the weather and clock, running on raspberry pi

import requests
from tkinter import Tk, Label
from datetime import datetime, timedelta, time

ACCUWEATHER_API_KEY_1 = ""
ACCUWEATHER_API_KEY_2 = ""
ACCUWEATHER_LOCATION_ID = ""

IPGEOLOCATION_API_KEY = ""
GEO_LAT = ""
GEO_LONG = ""

# IP address or domain name of raspberry pi / arduino / esp8266 etc
IOT_BOARD_URL = "" 

# API URLs
DISTRICT_WEATHER_API_URL = "http://dataservice.accuweather.com/currentconditions/v1/" + ACCUWEATHER_LOCATION_ID + "?apikey=" + ACCUWEATHER_API_KEY_1 + "&details=true"
CURRENT_WEATHER_API_URL = "http://" + IOT_BOARD_URL
ASTRONOMY_API_URL = "https://api.ipgeolocation.io/astronomy?apiKey=" + IPGEOLOCATION_API_KEY + "&lat=" + GEO_LAT + "&long=" + GEO_LONG
FORECAST_API_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/" + ACCUWEATHER_LOCATION_ID + "?apikey=" + ACCUWEATHER_API_KEY_2 + "&metric=true"

# Global variables to store astronomy, forecast, and district weather data
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
    "icon_phrase_day": "N/A",
    "icon_phrase_night": "N/A",
    "last_updated": None
}

district_weather_data = {
    "temperature": "N/A",
    "humidity": "N/A",
    "weather_text": "N/A",
    "last_updated": None
}

def is_daytime():
    sunrise, sunset, _, _ = get_astronomy_data()
    current_time = datetime.now().time()
    try:
        sunrise_time = datetime.strptime(sunrise, "%H:%M").time()
        sunset_time = datetime.strptime(sunset, "%H:%M").time()
        return sunrise_time <= current_time <= sunset_time
    except ValueError:
        print("Error parsing sunrise/sunset times. Using default hours.")
        day_start = time(6, 0)
        day_end = time(18, 0)
        return day_start <= current_time <= day_end

def fetch_current_weather_data():
    try:
        response = requests.get(CURRENT_WEATHER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        temperature = data["temperature"]
        humidity = data["humidity"]
        return temperature, humidity
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Error fetching current weather data: {e}")
        return None, None


def fetch_astronomy_data():
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
    global astronomy_data
    now = datetime.now()
    if astronomy_data["last_updated"] is None or now - astronomy_data["last_updated"] > timedelta(hours=4):
        fetch_astronomy_data()
    return (
        astronomy_data["sunrise"],
        astronomy_data["sunset"],
        astronomy_data["moonrise"],
        astronomy_data["moonset"]
    )

def fetch_forecast_data():
    global forecast_data
    response = requests.get(FORECAST_API_URL)
    if response.status_code == 200:
        data = response.json()
        daily_forecast = data["DailyForecasts"][0]
        forecast_data["min_temp"] = daily_forecast["Temperature"]["Minimum"]["Value"]
        forecast_data["max_temp"] = daily_forecast["Temperature"]["Maximum"]["Value"]
        forecast_data["icon_phrase_day"] = daily_forecast["Day"]["IconPhrase"]
        forecast_data["icon_phrase_night"] = daily_forecast["Night"]["IconPhrase"]
        forecast_data["last_updated"] = datetime.now()
    else:
        print(f"Forecast API Error: {response.status_code}")

def get_forecast_data():
    global forecast_data
    now = datetime.now()
    if forecast_data["last_updated"] is None or now - forecast_data["last_updated"] > timedelta(hours=4):
        fetch_forecast_data()
    if is_daytime():
        icon_phrase = forecast_data["icon_phrase_day"]
    else:
        icon_phrase = forecast_data["icon_phrase_night"]
    return (
        forecast_data["min_temp"],
        forecast_data["max_temp"],
        icon_phrase
    )

def fetch_district_weather_data():
    global district_weather_data
    response = requests.get(DISTRICT_WEATHER_API_URL)
    if response.status_code == 200:
        data = response.json()[0]
        district_weather_data["temperature"] = data["Temperature"]["Metric"]["Value"]
        district_weather_data["humidity"] = data["RelativeHumidity"]
        district_weather_data["weather_text"] = data["WeatherText"]
        district_weather_data["last_updated"] = datetime.now()
    else:
        print(f"District Weather API Error: {response.status_code}")

def get_district_weather_data():
    global district_weather_data
    now = datetime.now()
    if district_weather_data["last_updated"] is None or now - district_weather_data["last_updated"] > timedelta(minutes=30):
        fetch_district_weather_data()
    return (
        district_weather_data["temperature"],
        district_weather_data["humidity"],
        district_weather_data["weather_text"]
    )

def update_time():
    current_time = datetime.now()
    day = current_time.day
    month_abbr = current_time.strftime("%b").upper()
    year = current_time.strftime("%Y")
    weekday = current_time.strftime("%A")
    date_label.config(text=f"{day} {month_abbr} {year} ({weekday})")
    time_label.config(text=current_time.strftime("%H:%M"))
    root.after(1000, update_time)

def update_data():
    temperature, humidity = fetch_current_weather_data()
    if temperature is not None and humidity is not None:
        indoor_label.config(text=f"Home {temperature}°C {humidity}%")
    else:
        indoor_label.config(text="Error fetching data")

    sunrise, sunset, moonrise, moonset = get_astronomy_data()
    sun_label.config(text=f"Sunrise: {sunrise} Sunset: {sunset}")
    moon_label.config(text=f"Moonrise: {moonrise} Moonset {moonset}")

    min_temp, max_temp, icon_phrase = get_forecast_data()
    forecast_label.config(text=f"Forecast: {min_temp}°C ~ {max_temp}°C ({icon_phrase})")

    district_temp, district_humidity, weather_text = get_district_weather_data()
    district_weather_label.config(text=f"{district_temp}°C {district_humidity}% {weather_text}")

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
date_label = Label(root, font=("Helvetica", 36), fg="white", bg="#061f02")
date_label.pack(pady=10)

time_label = Label(root, font=("Helvetica", 100), fg="white", bg="#061f02")
time_label.pack(pady=10)

district_weather_label = Label(root, font=("Helvetica", 48), fg="white", bg="#061f02")
district_weather_label.pack(pady=10)

forecast_label = Label(root, font=("Helvetica", 24), fg="cyan", bg="#061f02")
forecast_label.pack(pady=10)

indoor_label = Label(root, font=("Helvetica", 46), fg="yellow", bg="#061f02")
indoor_label.pack()

sun_label = Label(root, font=("Helvetica", 24), fg="white", bg="#061f02")
sun_label.pack(pady=10)

moon_label = Label(root, font=("Helvetica", 24), fg="white", bg="#061f02")
moon_label.pack(pady=10)



# Start the display updates
update_time()
update_data()

root.mainloop()
