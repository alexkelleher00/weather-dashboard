import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import requests
import threading
import psutil
import socket
import datetime
import os

# === CONFIG ===
WEATHER_API_KEY = "7c5e741ce46b209653866485f0ab8ba7"
STORMGLASS_API_KEY = "8bfbc2a0-5ad7-11f0-bed1-0242ac130006-8bfbc304-5ad7-11f0-bed1-0242ac130006"
CITY = "Boston"
LAT = 42.4194      # Nahant Beach
LON = -70.9170

ICON_DIR = "icons"
GIF_DIR = "gifs"

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg="#101820")

        self.font_large = ("Arial", 48, "bold")
        self.font_medium = ("Arial", 32)
        self.font_small = ("Arial", 20)

        self.time_label = tk.Label(root, font=self.font_large, fg="white", bg="#101820")
        self.time_label.pack(pady=20)

        self.icon_frame = tk.Frame(root, bg="#101820")
        self.icon_frame.pack()

        self.day_night_label = tk.Label(self.icon_frame, bg="#101820")
        self.day_night_label.pack(side=tk.LEFT, padx=30)

        self.weather_icon_label = tk.Label(self.icon_frame, bg="#101820")
        self.weather_icon_label.pack(side=tk.LEFT, padx=30)

        self.weather_label = tk.Label(root, font=self.font_medium, fg="white", bg="#101820")
        self.weather_label.pack(pady=15)

        self.extended_ocean_frame = tk.Frame(root, bg="#101820")
        self.extended_ocean_frame.pack(pady=10)

        self.weather_info_frame = tk.Frame(self.extended_ocean_frame, bg="#101820")
        self.weather_info_frame.pack(side=tk.LEFT, padx=40)

        self.ocean_info_frame = tk.Frame(self.extended_ocean_frame, bg="#101820")
        self.ocean_info_frame.pack(side=tk.LEFT, padx=40)

        self.extended_weather_label = tk.Label(self.weather_info_frame, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.extended_weather_label.pack()

        self.ocean_label = tk.Label(self.ocean_info_frame, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.ocean_label.pack()


        self.system_label = tk.Label(root, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.system_label.pack(pady=10)

        self.status_label = tk.Label(root, font=self.font_small, fg="gray", bg="#101820")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        self.day_night_img = None
        self.gif_frames = []
        self.gif_index = 0

        self.update_time()
        self.update_weather()
        self.update_ocean_data()

    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.config(text=now.strftime("%A, %B %d %Y\n%I:%M:%S %p"))
        self.root.after(1000, self.update_time)

    def get_day_night_path(self):
        hour = datetime.datetime.now().hour
        return os.path.join(ICON_DIR, "sun.png" if 6 <= hour < 18 else "moon.png")

    def get_weather_gif_path(self, condition):
        cond = condition.lower()
        mapping = {
            'clear': 'clear.gif',
            'clouds': 'clouds.gif',
            'rain': 'rain.gif',
            'drizzle': 'drizzle.gif',
            'thunderstorm': 'thunderstorm.gif',
            'snow': 'snow.gif'
        }
        return os.path.join(GIF_DIR, mapping.get(cond, 'unknown.gif'))

    def animate_weather_icon(self):
        if not self.gif_frames:
            return
        frame = self.gif_frames[self.gif_index]
        self.weather_icon_label.config(image=frame)
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.root.after(100, self.animate_weather_icon)

    def update_weather(self):
        def fetch():
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=imperial"
                data = requests.get(url).json()

                if "main" in data:
                    temp = data["main"]["temp"]
                    cond = data["weather"][0]["main"]
                    humidity = data["main"]["humidity"]
                    clouds = data["clouds"]["all"]

                    self.weather_label.config(text=f"{CITY}\n{cond}, {temp:.1f}°F")

                    # Icons
                    dn = Image.open(self.get_day_night_path()).resize((100, 100))
                    self.day_night_img = ImageTk.PhotoImage(dn)
                    self.day_night_label.config(image=self.day_night_img)

                    gif = Image.open(self.get_weather_gif_path(cond))
                    self.gif_frames = [ImageTk.PhotoImage(frame.resize((100, 100))) for frame in ImageSequence.Iterator(gif)]
                    self.gif_index = 0
                    self.animate_weather_icon()

                    # UV + Dew Point
                    uv_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly,daily,alerts&appid={WEATHER_API_KEY}&units=imperial"
                    uv_data = requests.get(uv_url).json()
                    uvi = uv_data.get("current", {}).get("uvi", "N/A")
                    dew_point = uv_data.get("current", {}).get("dew_point", "N/A")

                    extended_text = (
                        f"Humidity: {humidity}%\n"
                        f"Cloud Cover: {clouds}%\n"
                        f"UV Index: {uvi}\n"
                        f"Dew Point: {dew_point}°F"
                    )
                    self.extended_weather_label.config(text=extended_text)
                else:
                    self.weather_label.config(text="Weather unavailable")
                    self.extended_weather_label.config(text="")
            except Exception:
                self.weather_label.config(text="Error fetching weather")
                self.extended_weather_label.config(text="")

        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(600000, self.update_weather)

    def update_ocean_data(self):
        def deg_to_compass(deg):
            directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            return directions[int((deg / 45) + 0.5) % 8]

        def c_to_f(celsius):
            return (celsius * 9 / 5) + 32

        def fetch():
            try:
                now = datetime.datetime.now(datetime.timezone.utc)
                start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                end = (now + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

                headers = {'Authorization': STORMGLASS_API_KEY}

                # Wave/weather data
                weather_url = (
                    f"https://api.stormglass.io/v2/weather/point?"
                    f"lat={LAT}&lng={LON}&params=waveHeight,swellHeight,waterTemperature,windSpeed,windDirection"
                    f"&source=noaa&start={start}&end={end}"
                )
                print("Fetching weather data...")
                weather_response = requests.get(weather_url, headers=headers)
                print("Weather status:", weather_response.status_code)

                if weather_response.status_code != 200:
                    print("Weather response text:", weather_response.text)
                    raise Exception("Weather API call failed")

                weather_data = weather_response.json()
                print("Weather JSON received.")

                wave = swell = water_temp_c = wind_speed = wind_dir = None
                if "hours" in weather_data and len(weather_data["hours"]) > 0:
                    hour_data = weather_data["hours"][0]
                    wave = hour_data.get('waveHeight', {}).get('noaa', 0.0)
                    swell = hour_data.get('swellHeight', {}).get('noaa', 0.0)
                    water_temp_c = hour_data.get('waterTemperature', {}).get('noaa', 0.0)
                    wind_speed = hour_data.get('windSpeed', {}).get('noaa', 0.0)
                    wind_dir_deg = hour_data.get('windDirection', {}).get('noaa')
                    wind_dir = deg_to_compass(wind_dir_deg) if wind_dir_deg is not None else "N/A"

                # Tide data
                tide_url = (
                    f"https://api.stormglass.io/v2/tide/extremes/point?"
                    f"lat={LAT}&lng={LON}&start={start}&end={end}"
                )
                print("Fetching tide data...")
                tide_response = requests.get(tide_url, headers=headers)
                print("Tide status:", tide_response.status_code)

                if tide_response.status_code != 200:
                    print("Tide response text:", tide_response.text)
                    raise Exception("Tide API call failed")

                tide_data = tide_response.json()
                print("Tide JSON received.")

                next_tide_text = "Tide data unavailable"
                if "data" in tide_data and len(tide_data["data"]) > 0:
                    tide_event = tide_data["data"][0]
                    tide_type = tide_event.get("type", "unknown").capitalize()
                    tide_height = tide_event.get("height", 0.0)
                    tide_time = datetime.datetime.fromisoformat(tide_event["time"].replace("Z", "+00:00"))
                    tide_time_str = tide_time.strftime("%I:%M %p")
                    next_tide_text = f"Next Tide: {tide_type} at {tide_time_str} ({tide_height:.2f} m)"

                water_temp_f = c_to_f(water_temp_c)
                ocean_text = (
                    f"Nahant Beach Conditions:\n"
                    f"Wave Height: {wave:.1f} m\n"
                    f"Swell Height: {swell:.1f} m\n"
                    f"Water Temp: {water_temp_f:.1f} °F\n"
                    f"Wind: {wind_speed:.1f} m/s {wind_dir}\n"
                    f"{next_tide_text}"
                )

                self.ocean_label.config(text=ocean_text)

            except Exception as e:
                print("Ocean fetch error:", e)
                self.ocean_label.config(text="Error fetching ocean data")

        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(3600000 * 3, self.update_ocean_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
