from dotenv import load_dotenv
import os
import base64
from requests import post
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
import queue
import time
from config import settings

SPOTIFY_SCOPE = "user-top-read user-read-playback-state user-modify-playback-state"
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")


class SpotifyController:
    def __init__(self):
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=REDIRECT_URI,
                scope=SPOTIFY_SCOPE,
            )
        )

        self.device_id = None
        self.q: "queue.Queue[str]" = queue.Queue()
        self.lock = threading.Lock()
        self.last_ts = 0.0
        self.interval = settings.INTERVAL
        self.state = "unknown"
        self.state_ts = 0.0
        self.state_ttl = 2.0
        self.ensure_device()
        self.worker = threading.Thread(target=self.run_worker, daemon=True)
        self.worker.start()

    def ensure_device(self):
        try:
            devices = self.sp.devices()
            for d in devices.get("devices", []):
                if d.get("is_active"):
                    self.device_id = d["id"]
                    return
            if devices.get("devices"):
                self.device_id = devices["devices"][0]["id"]
        except Exception:
            self.device_id = None

    def wait_device(self, timeout: float = 5.0, interval: float = 0.5) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            self.ensure_device()
            if self.device_id:
                return True
            time.sleep(interval)
        return False

    def throttled(self) -> bool:
        with self.lock:
            now = time.time()
            if now - self.last_ts < self.interval:
                return True
            self.last_ts = now
            return False

    def refresh_state(self):
        try:
            pb = self.sp.current_playback()
            if pb and pb.get("is_playing"):
                self.state = "playing"
            elif pb:
                self.state = "paused"
            else:
                self.state = "unknown"
            self.state_ts = time.time()
        except Exception:
            self.state = "unknown"
            self.state_ts = time.time()

    def run_cmd(self, cmd: str):
        try:
            if cmd == "refresh":
                self.refresh_state()
                return

            if not self.device_id:
                self.wait_device()
            if not self.device_id:
                print("Spotify: No active device found. Open Spotify and try again.")
                return

            if cmd == "play_top":
                try:
                    self.sp.transfer_playback(self.device_id, force_play=True)
                except Exception:
                    pass
                top = self.sp.current_user_top_tracks(limit=1, time_range="short_term")
                if top.get("items"):
                    uri = top["items"][0]["uri"]
                    self.sp.start_playback(device_id=self.device_id, uris=[uri])
                    self.state = "playing"
                    self.state_ts = time.time()
                else:
                    print("Spotify: No top tracks available to play.")
            elif cmd == "pause":
                self.sp.pause_playback(device_id=self.device_id)
                self.state = "paused"
                self.state_ts = time.time()
            elif cmd == "next":
                self.sp.next_track(device_id=self.device_id)
                self.state = "playing"
                self.state_ts = time.time()
            elif cmd == "prev":
                self.sp.previous_track(device_id=self.device_id)
                self.state = "playing"
                self.state_ts = time.time()
            elif cmd == "resume":
                self.sp.start_playback(device_id=self.device_id)
                self.state = "playing"
                self.state_ts = time.time()
        except spotipy.exceptions.SpotifyException as se:
            print(f"Spotify command error: {se}")
        except Exception:
            pass

    def run_worker(self):
        while True:
            cmd = self.q.get()
            self.run_cmd(cmd)


    def get_state(self) -> str:
        if time.time() - self.state_ts > self.state_ttl:
            try:
                self.q.put_nowait("refresh")
            except Exception:
                pass
        return self.state

    def play_top(self):
        if self.throttled():
            return
        try:
            self.q.put_nowait("play_top")
        except Exception:
            pass

    def pause(self):
        if self.throttled():
            return
        try:
            self.q.put_nowait("pause")
        except Exception:
            pass

    def next(self):
        if self.throttled():
            return
        try:
            self.q.put_nowait("next")
        except Exception:
            pass

    def prev(self):
        if self.throttled():
            return
        try:
            self.q.put_nowait("prev")
        except Exception:
            pass

    def resume(self):
        if self.throttled():
            return
        try:
            self.q.put_nowait("resume")
        except Exception:
            pass

controller = SpotifyController()


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
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result.get("access_token")
    return token


def get_spotify_client():
    return controller.sp


def get_playback_state():
    return controller.get_state()


def play_top_track():
    return controller.play_top()


def pause_track():
    return controller.pause()


def next_track():
    return controller.next()


def previous_track():
    return controller.prev()


def resume_track():
    return controller.resume()
