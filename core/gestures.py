import cv2 as cv
import mediapipe as mp
import numpy as np
from config import mappings, settings
import time

class Gestures:
    def __init__(self):
        self.last_finger_count = None
        self.last_time = time.time()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=settings.MAX_HANDS,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self._tip_ids = [4, 8, 12, 16, 20]

    def process_frame(self, frame: np.ndarray) -> tuple:
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        try:
            rgb_frame.setflags(write=False)
        except Exception:
            pass
        results = self.hands.process(rgb_frame)
        try:
            rgb_frame.setflags(write=True)
        except Exception:
            pass
        return results, rgb_frame

    def find_fingers(self, frame: np.ndarray, results=None, draw=True) -> np.ndarray:
        if results is None:
            results, _ = self.process_frame(frame)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                if draw:
                    self.mp_drawing.draw_landmarks(frame, handLms, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def count_fingers_up(self, frame: np.ndarray, results=None) -> list:
        if results is None:
            results, _ = self.process_frame(frame)
        fingers_up = []
        tip_ids = self._tip_ids
        if results.multi_hand_landmarks:
            handedness = []
            if results.multi_handedness:
                handedness = [h.classification[0].label for h in results.multi_handedness]
            h, w = frame.shape[:2]
            for idx, handLms in enumerate(results.multi_hand_landmarks):
                lm_list = []
                for id, lm in enumerate(handLms.landmark):
                    lm_list.append((int(lm.x * w), int(lm.y * h)))
                fingers = []
                if len(lm_list) >= 21:
                    if handedness and handedness[idx] == 'Right':
                        fingers.append(1 if lm_list[tip_ids[0]][0] < lm_list[tip_ids[0] - 1][0] else 0)
                    else:
                        fingers.append(1 if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0] - 1][0] else 0)
                    for i in range(1, 5):
                        fingers.append(1 if lm_list[tip_ids[i]][1] < lm_list[tip_ids[i] - 2][1] else 0)
                    fingers_up.append(sum(fingers))
        return fingers_up

    def map_fingers_to_action(self, finger_count):
        current_time = time.time()
        if finger_count != self.last_finger_count:
            self.last_finger_count = finger_count
            self.last_time = current_time
            return {'text': 'UNKNOWN', 'color': (255, 255, 255), 'action': None}
        elif current_time - self.last_time >= 0.5:
            action = mappings.get_action_by_finger_count(finger_count)
            display_info = mappings.get_display_info(action)
            display_info = {**display_info, 'action': action}
            return display_info
        else:
            return {'text': 'UNKNOWN', 'color': (255, 255, 255), 'action': None}
