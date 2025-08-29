import cv2 as cv
import mediapipe as mp
from config import mappings, settings

class Gestures:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=settings.MAX_HANDS,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame: 'np.ndarray') -> tuple:
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results, rgb_frame

    def find_fingers(self, frame: 'np.ndarray', results=None, draw=True) -> 'np.ndarray':
        if results is None:
            results, _ = self.process_frame(frame)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                if draw:
                    self.mp_drawing.draw_landmarks(frame, handLms, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def count_fingers_up(self, frame: 'np.ndarray', results=None) -> list:
        if results is None:
            results, _ = self.process_frame(frame)
        fingers_up = []
        tip_ids = [4, 8, 12, 16, 20]
        if results.multi_hand_landmarks:
            handedness = []
            if results.multi_handedness:
                handedness = [h.classification[0].label for h in results.multi_handedness]
            for idx, handLms in enumerate(results.multi_hand_landmarks):
                lm_list = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, _ = frame.shape
                    lm_list.append((int(lm.x * w), int(lm.y * h)))
                fingers = []
                if len(lm_list) >= 21:
                    if handedness and handedness[idx] == 'Right':
                        if lm_list[tip_ids[0]][0] < lm_list[tip_ids[0] - 1][0]:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    else:
                        if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0] - 1][0]:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    for i in range(1, 5):
                        if lm_list[tip_ids[i]][1] < lm_list[tip_ids[i] - 2][1]:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    fingers_up.append(sum(fingers))
        return fingers_up

    def map_fingers_to_action(self, finger_count):
        #TODO: only accept a gesture after 1.5 second
        action = mappings.get_action_by_finger_count(finger_count)
        display_info = mappings.get_display_info(action)
        return display_info
