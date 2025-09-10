from dotenv import load_dotenv
import os
import base64
from requests import post
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#TODO: integrate hand gestures in music playing
def get_token():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
         "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    print(token)
    return token

SPOTIFY_SCOPE = "user-top-read user-read-playback-state user-modify-playback-state"
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")


def get_spotify_client():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))
    return sp

def get_active_device(sp):
    devices = sp.devices()
    for device in devices.get('devices', []):
        if device.get('is_active'):
            return device['id']
    if devices.get('devices'):
        return devices['devices'][0]['id']
    return None

#currently starting top track but can be changed to a specific song/playlist
def play_top_track():
    sp = get_spotify_client()
    try:
        top_tracks = sp.current_user_top_tracks(limit=1, time_range='short_term')
        if top_tracks['items']:
            track_uri = top_tracks['items'][0]['uri']
            print(f"Playing: {top_tracks['items'][0]['name']} by {top_tracks['items'][0]['artists'][0]['name']}")
            device_id = get_active_device(sp)
            if device_id:
                sp.start_playback(device_id=device_id, uris=[track_uri])
            else:
                print("No active Spotify device found.")
        else:
            print("No top tracks found.")
    except Exception as e:
        print(f"Spotify play error: {e}")

def pause_track():
    sp = get_spotify_client()
    try:
        device_id = get_active_device(sp)
        if device_id:
            sp.pause_playback(device_id=device_id)
        else:
            print("No active Spotify device found.")
    except Exception as e:
        print(f"Spotify pause error: {e}")

def next_track():
    sp = get_spotify_client()
    try:
        device_id = get_active_device(sp)
        if device_id:
            sp.next_track(device_id=device_id)
        else:
            print("No active Spotify device found.")
    except Exception as e:
        print(f"Spotify next error: {e}")

def previous_track():
    sp = get_spotify_client()
    try:
        device_id = get_active_device(sp)
        if device_id:
            sp.previous_track(device_id=device_id)
        else:
            print("No active Spotify device found.")
    except Exception as e:
        print(f"Spotify previous error: {e}")
