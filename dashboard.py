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
CITY = "Boston"
ICON_DIR = "icons"       # static PNG icons (sun.png, moon.png)
GIF_DIR = "gifs"         # animated GIFs (clear.gif, rain.gif, etc.)

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg="#101820")

        self.font_large = ("Arial", 36, "bold")
        self.font_medium = ("Arial", 24)
        self.font_small = ("Arial", 14)

        self.time_label = tk.Label(root, font=self.font_large, fg="white", bg="#101820")
        self.time_label.pack(pady=10)

        self.icon_frame = tk.Frame(root, bg="#101820")
        self.icon_frame.pack()

        self.day_night_label = tk.Label(self.icon_frame, bg="#101820")
        self.day_night_label.pack(side=tk.LEFT, padx=20)

        self.weather_icon_label = tk.Label(self.icon_frame, bg="#101820")
        self.weather_icon_label.pack(side=tk.LEFT, padx=20)

        self.weather_label = tk.Label(root, font=self.font_medium, fg="white", bg="#101820")
        self.weather_label.pack(pady=10)

        self.system_label = tk.Label(root, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.system_label.pack(pady=10)

        self.status_label = tk.Label(root, font=self.font_small, fg="gray", bg="#101820")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        self.day_night_img = None
        self.gif_frames = []
        self.gif_index = 0

        self.update_time()
        self.update_weather()
        self.update_system_info()

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
            'drizzle': 'rain.gif',
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
                    self.weather_label.config(text=f"{CITY}\n{cond}, {temp:.1f}°F")

                    # Day/night icon
                    dn = Image.open(self.get_day_night_path()).resize((80, 80))
                    self.day_night_img = ImageTk.PhotoImage(dn)
                    self.day_night_label.config(image=self.day_night_img)

                    # Animated weather GIF
                    gif = Image.open(self.get_weather_gif_path(cond))
                    self.gif_frames = [ImageTk.PhotoImage(frame.resize((80,80))) for frame in ImageSequence.Iterator(gif)]
                    self.gif_index = 0
                    self.animate_weather_icon()
                else:
                    self.weather_label.config(text="Weather unavailable")

            except Exception:
                self.weather_label.config(text="Error fetching weather")

        threading.Thread(target=fetch, daemon=True).start()
        self.root.after(600000, self.update_weather)

    def update_system_info(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "N/A"
        self.system_label.config(text=f"CPU Usage: {cpu}%\nMemory Usage: {mem}%\nDisk Usage: {disk}%\nLocal IP: {ip}")
        self.root.after(5000, self.update_system_info)

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
