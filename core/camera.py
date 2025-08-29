import cv2 as cv
from config import settings


class Camera:
    def __init__(self):
        self.cap = None

    def initialize(self):
        self.cap = cv.VideoCapture(settings.CAMERA_INDEX)
        if not self.cap.isOpened():
            print("Cannot open camera")
            return False

        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, settings.FRAME_WIDTH)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, settings.FRAME_HEIGHT)
        return True

    def get_frame(self):
        if not self.cap:
            print("Camera not initialized")
            return
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Cannot receive frame")
                break
            yield frame

    def release(self):
        if self.cap:
            self.cap.release()
        cv.destroyAllWindows()
        print("Camera released, windows closed")
