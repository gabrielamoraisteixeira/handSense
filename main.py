from core import Camera, Gestures
from config import settings
import cv2 as cv

def main():
    cam = Camera()
    cam.initialize()
    gestures = Gestures()
    try:
        for frame in cam.get_frame():
            results, _ = gestures.process_frame(frame)
            processed_frame = gestures.find_fingers(frame, results=results, draw=True)
            cv.imshow(settings.WINDOW_TITLE, processed_frame)
            fingers_up = gestures.count_fingers_up(frame, results=results)
            print(fingers_up)
            if cv.waitKey(1) & 0xFF == ord(settings.EXIT_KEY):
                break
    finally:
        cam.release()

if __name__ == '__main__':
    main()
