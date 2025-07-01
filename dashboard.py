import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import time
import threading
import psutil
import socket
import datetime

# === CONFIG ===
WEATHER_API_KEY = "7c5e741ce46b209653866485f0ab8ba7"
CITY = "Boston"

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#101820")

        self.font_large = ("Arial", 36, "bold")
        self.font_medium = ("Arial", 24)
        self.font_small = ("Arial", 14)

        self.time_label = tk.Label(root, font=self.font_large, fg="white", bg="#101820")
        self.time_label.pack(pady=10)

        self.weather_label = tk.Label(root, font=self.font_medium, fg="white", bg="#101820")
        self.weather_label.pack(pady=10)

        self.system_label = tk.Label(root, font=self.font_small, fg="white", bg="#101820", justify=tk.LEFT)
        self.system_label.pack(pady=10)

        self.status_label = tk.Label(root, font=self.font_small, fg="gray", bg="#101820")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        self.update_time()
        self.update_weather()
        self.update_system_info()

    def update_time(self):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%A, %B %d %Y\n%I:%M:%S %p")
        self.time_label.config(text=formatted_time)
        self.root.after(1000, self.update_time)

    def update_weather(self):
        def fetch_weather():
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=imperial"
                response = requests.get(url)
                data = response.json()

                if data.get("main"):
                    temp = data["main"]["temp"]
                    condition = data["weather"][0]["main"]
                    weather_text = f"{CITY}\n{condition}, {temp:.1f}°F"
                else:
                    weather_text = "Weather unavailable"
            except Exception as e:
                weather_text = f"Error fetching weather"

            self.weather_label.config(text=weather_text)

        threading.Thread(target=fetch_weather, daemon=True).start()
        self.root.after(600000, self.update_weather)  # every 10 minutes

    def update_system_info(self):
        def fetch_system_info():
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                ip = socket.gethostbyname(socket.gethostname())

                info = (
                    f"CPU Usage: {cpu}%\n"
                    f"Memory Usage: {mem}%\n"
                    f"Disk Usage: {disk}%\n"
                    f"Local IP: {ip}"
                )
            except Exception as e:
                info = "System info error"

            self.system_label.config(text=info)

        fetch_system_info()
        self.root.after(5000, self.update_system_info)  # every 5 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
