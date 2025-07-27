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
SPOTIFY_CLIENT_SECRET = "591a0dd14de549ef90b505adfb6e1388"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SPOTIFY_PLAYLIST_URI = "spotify:playlist:2lsjZmZSeeSERMKq8ARG6h"
SPOTIFY_DJX_URI = "spotify:track:6wOmmoM5nyS6mOyzo9wDjC?si=95e2c80b09b649b4"  # Replace with actual DJ X URI

class SpotifyTouchTunes:
    def __init__(self, root, back_callback):
        self.root = root
        self.back_callback = back_callback
        self.root.configure(bg="#101820")
        self.sp = None
        self.current_track = None
        self.album_img = None
        self.shuffle_state = False

        self.setup_gui()
        self.init_spotify()
        self.start_playback()
        self.update_track_info()
        self.show_device_buttons()
        self.load_playlists()

    def setup_gui(self):
        self.album_label = tk.Label(self.root, bg="#101820")
        self.album_label.pack(pady=20)

        self.track_label = tk.Label(self.root, font=("Arial", 24), fg="white", bg="#101820")
        self.track_label.pack(pady=10)

        self.artist_label = tk.Label(self.root, font=("Arial", 18), fg="gray", bg="#101820")
        self.artist_label.pack(pady=5)

        self.controls = tk.Frame(self.root, bg="#101820")
        self.controls.pack(pady=20)

        self.skip_prev_button = tk.Button(self.controls, text="⏮️ Prev", font=("Arial", 20), command=self.skip_previous)
        self.skip_prev_button.grid(row=3, column=0, padx=10, pady=10)

        self.play_pause_button = tk.Button(self.controls, text="▶️", font=("Arial", 20), command=self.toggle_playback)
        self.play_pause_button.grid(row=3, column=1, padx=10, pady=10)

        self.skip_next_button = tk.Button(self.controls, text="⏭️ Next", font=("Arial", 20), command=self.skip_next)
        self.skip_next_button.grid(row=3, column=2, padx=10, pady=10)

        self.shuffle_button = tk.Button(self.controls, text="🔀 Shuffle Off", font=("Arial", 14), command=self.toggle_shuffle)
        self.shuffle_button.grid(row=3, column=3, padx=10, pady=10)

        self.back_button = tk.Button(self.controls, text="Back", command=self.back_callback)
        self.back_button.grid(row=3, column=4, padx=10, pady=10)

    def init_spotify(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="user-read-playback-state user-modify-playback-state user-library-read",
            cache_path=".spotify_cache"
        ))

    def start_playback(self):
        devices = self.sp.devices().get('devices', [])
        if not devices:
            print("No devices found.")
            return

        device_id = devices[0]['id']
        try:
            self.sp.start_playback(device_id=device_id)
        except spotipy.SpotifyException as e:
            print(f"Error starting playback: {e}")

    def toggle_playback(self):
        playback = self.sp.current_playback()
        if playback and playback['is_playing']:
            self.sp.pause_playback()
            self.play_pause_button.config(text="▶️")
        else:
            self.sp.start_playback()
            self.play_pause_button.config(text="⏸️")

    def toggle_shuffle(self):
        self.shuffle_state = not self.shuffle_state
        self.sp.shuffle(state=self.shuffle_state)
        text = "🔀 Shuffle On" if self.shuffle_state else "🔀 Shuffle Off"
        self.shuffle_button.config(text=text)

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

    def skip_next(self):
        try:
            self.sp.next_track()
        except Exception as e:
            print("Skip Next Error:", e)

    def skip_previous(self):
        try:
            self.sp.previous_track()
        except Exception as e:
            print("Skip Previous Error:", e)

    def show_device_buttons(self):
        try:
            devices = self.sp.devices().get('devices', [])
            if not devices:
                print("No devices found.")
                return

            tk.Label(self.controls, text="Available Devices:", font=("Arial", 14), fg="white", bg="#101820").grid(row=4,column=4, padx=10, pady=10)

            for i, device in enumerate(devices):
                btn = tk.Button(
                    self.controls,
                    text=device['name'],
                    command=lambda d_id=device['id']: self.transfer_to_device(d_id),
                    bg="#1DB954", fg="white", font=("Arial", 12)
                )
                btn.grid(row=4,column=5+i, padx=10, pady=10)
        except Exception as e:
            print("Device fetch error:", e)

    def transfer_to_device(self, device_id):
        try:
            self.sp.transfer_playback(device_id, force_play=True)
            print(f"Transferred playback to {device_id}")
        except Exception as e:
            print("Transfer error:", e)

    def load_playlists(self):
        try:
            playlists = self.sp.current_user_playlists(limit=20)['items']
            tk.Label(self.controls, text="Playlists: ", font=("Arial", 14), fg="white", bg="#101820").grid(row=4,column=0, padx=10, pady=10)

            liked_button = tk.Button(self.controls, text="❤️ Liked Songs", command=self.play_liked_songs, bg="#535353", fg="white")
            liked_button.grid(row=4, column=1, padx=10, pady=10)

            djx_button = tk.Button(self.controls, text="🎧 Mumford Mansfield", command=lambda: self.play_playlist(SPOTIFY_PLAYLIST_URI), bg="#1DB954", fg="white")
            djx_button.grid(row=4, column=2, padx=10, pady=10)
            for playlist in playlists:
                name = playlist['name']
                if name == "Español dos":
                    uri = playlist['uri']
                    btn = tk.Button(self.controls, text=name, command=lambda u=uri: self.play_playlist(u), bg="#333", fg="white")
                    btn.grid(row=4, column=3, padx=10, pady=10)
        except Exception as e:
            print("Load Playlists Error:", e)

    def play_playlist(self, playlist_uri):
        devices = self.sp.devices().get('devices', [])
        if not devices:
            print("No devices found.")
            return
        device_id = devices[0]['id']
        self.sp.start_playback(device_id=device_id, context_uri=playlist_uri)

    def play_liked_songs(self):
        try:
            results = self.sp.current_user_saved_tracks(limit=50)
            track_uris = [item['track']['uri'] for item in results['items']]
            if not track_uris:
                print("No liked songs found.")
                return

            devices = self.sp.devices().get('devices', [])
            if not devices:
                print("No devices found.")
                return
            device_id = devices[0]['id']
            self.sp.start_playback(device_id=device_id, uris=track_uris)
        except Exception as e:
            print("Error playing liked songs:", e)
