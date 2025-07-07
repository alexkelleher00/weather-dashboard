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

        self.extended_weather_label = tk.Label(root, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.extended_weather_label.pack(pady=5)

        self.ocean_label = tk.Label(root, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.ocean_label.pack(pady=10)

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
        def fetch():
            try:
                now = datetime.datetime.utcnow().isoformat() + 'Z'
                headers = {'Authorization': STORMGLASS_API_KEY}
                url = (
                    f"https://api.stormglass.io/v2/weather/point?"
                    f"lat={LAT}&lng={LON}&params=waveHeight,swellHeight,waterTemperature"
                    f"&source=noaa&start={now}&end={now}"
                )
                response = requests.get(url, headers=headers)
                data = response.json()

                if 'hours' in data and len(data['hours']) > 0:
                    hour_data = data['hours'][0]
                    wave = hour_data.get('waveHeight', {}).get('noaa', None)
                    swell = hour_data.get('swellHeight', {}).get('noaa', None)
                    water_temp = hour_data.get('waterTemperature', {}).get('noaa', None)

                    ocean_text = (
                        f"Nahant Beach Conditions:\n"
                        f"Wave Height: {wave:.1f} m\n"
                        f"Swell Height: {swell:.1f} m\n"
                        f"Water Temp: {water_temp:.1f} °C"
                    )
                    self.ocean_label.config(text=ocean_text)
                else:
                    self.ocean_label.config(text="Ocean data unavailable")

            except Exception as e:
                self.ocean_label.config(text="Error fetching wave data")

        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(900000, self.update_ocean_data)  # update every 15 mins

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
