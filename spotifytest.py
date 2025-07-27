import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "e2b66ba1e9f4437183f74f37fe9bfbee"
SPOTIFY_CLIENT_SECRET = "591a0dd14de549ef90b505adfb6e1388"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SPOTIFY_PLAYLIST_URI = "spotify:playlist:2lsjZmZSeeSERMKq8ARG6h?si=f87c0c9137f049cb"  # Replace with your playlist

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="user-read-playback-state user-modify-playback-state"
        ))

devices = sp.devices()
for device in devices['devices']:
    print(f"Name: {device['name']}, ID: {device['id']}")

