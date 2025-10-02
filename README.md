# HandSense

HandSense is a simple project that transforms your webcam into a smart controller for Spotify, letting you play, pause, and skip tracks with simple hand gestures. By combining computer vision (OpenCV, MediaPipe) with the Spotify API.

## Gesture Mapping

HandSense maps the number of fingers you show to specific music control actions:

| Fingers Up | Action    |
|------------|-----------|
| 0          | Pause     |
| 1          | Previous  |
| 2          | Next      |
| 5          | Play/Resume |

When you show a gesture, the system detects the number of fingers and triggers the corresponding Spotify action. For example, showing 0 fingers will pause playback, while showing 5 will play or resume the current track.

## Setup

1. **Clone the repository**  


2. **Run the setup script**  
   The provided `setup.sh` script will create a Python virtual environment and install all dependencies:
   ```sh
   ./setup.sh
   ```

   **On Windows, run the commands in setup.sh manually.**


3. **Configure Spotify credentials**  
   Set your Spotify API credentials as environment variables. You can do this by creating a `.env` file in the project root with the following content:
   ```env
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   ```
   Or export them in your shell before running the app:
   ```sh
   export CLIENT_ID=your_spotify_client_id
   export CLIENT_SECRET=your_spotify_client_secret
   ```

## Usage

Run the main application:
```sh
python main.py
```
Show your hand to the webcam and use gestures to control playback.

## Notes

- Requires a working webcam.
- Spotify account and API credentials needed.
