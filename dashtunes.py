import tkinter as tk
from PIL import Image, ImageTk
import requests
import io
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
import subprocess
import time

# === CONFIG ===
BLUETOOTH_DEVICE_NAME = "DJ Kells"
SPOTIFY_CLIENT_ID = "e2b66ba1e9f4437183f74f37fe9bfbee"
SPOTIFY_CLIENT_SECRET = "591a0dd14de549ef90b505adfb6e1388t"
SPOTIFY_REDIRECT_URI = "https://localhost:8888/callback"
SPOTIFY_PLAYLIST_URI = "spotify:playlist:2lsjZmZSeeSERMKq8ARG6h?si=f87c0c9137f049cb"  # Replace with your playlist

class SpotifyTouchTunes:
    def __init__(self, root, back_callback):
        self.root = root
        self.back_callback = back_callback
        self.root.configure(bg="#101820")
        self.sp = None
        self.current_track = None
        self.album_img = None

        self.setup_gui()
        self.connect_bluetooth()
        self.init_spotify()
        self.start_playback()
        self.update_track_info()

    def setup_gui(self):
        self.album_label = tk.Label(self.root, bg="#101820")
        self.album_label.pack(pady=20)

        self.track_label = tk.Label(self.root, font=("Arial", 24), fg="white", bg="#101820")
        self.track_label.pack(pady=10)

        self.artist_label = tk.Label(self.root, font=("Arial", 18), fg="gray", bg="#101820")
        self.artist_label.pack(pady=5)

        self.controls = tk.Frame(self.root, bg="#101820")
        self.controls.pack(pady=20)

        self.play_button = tk.Button(self.controls, text="Pause", command=self.toggle_playback)
        self.play_button.pack(side=tk.LEFT, padx=10)

        self.back_button = tk.Button(self.controls, text="Back", command=self.back_callback)
        self.back_button.pack(side=tk.LEFT, padx=10)

    def connect_bluetooth(self):
        def run():
            print("Connecting to Bluetooth speaker...")
            try:
                subprocess.run(f"bluetoothctl connect $(bluetoothctl devices | grep '{BLUETOOTH_DEVICE_NAME}' | awk '{{print $2}}')", shell=True, check=True)
                print("Bluetooth speaker connected.")
            except subprocess.CalledProcessError:
                print("Bluetooth connection failed.")
        threading.Thread(target=run, daemon=True).start()

    def init_spotify(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="user-read-playback-state user-modify-playback-state"
        ))

    def start_playback(self):
        devices = self.sp.devices().get('devices', [])
        if not devices:
            print("No devices found.")
            return

        device_id = devices[0]['id']
        try:
            self.sp.start_playback(device_id=device_id, context_uri=SPOTIFY_PLAYLIST_URI)
        except spotipy.SpotifyException as e:
            print(f"Error starting playback: {e}")

    def toggle_playback(self):
        playback = self.sp.current_playback()
        if playback and playback['is_playing']:
            self.sp.pause_playback()
            self.play_button.config(text="Play")
        else:
            self.sp.start_playback()
            self.play_button.config(text="Pause")

    def update_track_info(self):
        def run():
            while True:
                try:
                    current = self.sp.current_playback()
                    if current and current['item']:
                        item = current['item']
                        if item['id'] != self.current_track:
                            self.current_track = item['id']
                            name = item['name']
                            artist = ", ".join([a['name'] for a in item['artists']])
                            img_url = item['album']['images'][0]['url']

                            response = requests.get(img_url)
                            img_data = Image.open(io.BytesIO(response.content)).resize((300, 300))
                            self.album_img = ImageTk.PhotoImage(img_data)
                            self.album_label.config(image=self.album_img)
                            self.track_label.config(text=name)
                            self.artist_label.config(text=artist)
                except Exception as e:
                    print("Error updating track info:", e)

                time.sleep(5)

        threading.Thread(target=run, daemon=True).start()
