import cv2 as cv
from config import settings, mappings
from core import Camera, Gestures, spotify_player as sp
def main():
    cam = Camera()
    cam.initialize()
    gestures = Gestures()
    try:
        for frame in cam.get_frame():
            results, _ = gestures.process_frame(frame)
            processed_frame = gestures.find_fingers(frame, results=results, draw=True)
            processed_frame = cv.flip(processed_frame, 1)
            fingers_up = gestures.count_fingers_up(frame, results=results)
            if fingers_up:
                display_info = gestures.map_fingers_to_action(fingers_up[0])
                action = mappings.get_action_by_finger_count(fingers_up[0])
                if action == 'play':
                    sp.play_top_track()
                elif action == 'pause':
                    sp.pause_track()
                elif action == 'next':
                    sp.next_track()
                else:
                    sp.previous_track()
            else:
                display_info = {'text': 'UNKNOWN', 'color': (255, 255, 255)}
            cv.putText(
            processed_frame,
            display_info['text'],
            (30, 60),
            cv.FONT_HERSHEY_SIMPLEX,
            2,
            display_info['color'],
            4,
            cv.LINE_AA
            )
            cv.imshow(settings.WINDOW_TITLE, processed_frame)
            print(fingers_up)
            if cv.waitKey(1) & 0xFF == ord(settings.EXIT_KEY):
                break
    finally:
        cam.release()

if __name__ == '__main__':
    sp.play_top_track()
    sp.get_token()
    main()
