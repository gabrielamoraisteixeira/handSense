import cv2 as cv


class Camera:
    def __init__(self):
        self.cap = None

    def initialize(self):
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            return False
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Cannot receive frame")
                    break
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                cv.imshow('Camera (Press Q to exit)', gray)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.release()

    def release(self):
        if self.cap:
            self.cap.release()
        cv.destroyAllWindows()
        print("Camera released, windows closed")
