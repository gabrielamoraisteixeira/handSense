
GESTURES_MAPPING = {
    'pause': 0,
    'play': 5,
    'next': 2,
    'previous': 1,
    }

GESTURES_DISPLAY = {
    'pause': {
        'text': 'PAUSE',
        'color': (0, 255, 255)
    },
    'play': {
        'text': 'PLAY',
        'color': (0, 255, 0)
    },
    'next': {
        'text': 'NEXT',
        'color': (255, 0, 0)
    },
    'previous': {
        'text': 'PREVIOUS',
        'color': (255, 0, 255)
    },
    }

def get_action_by_finger_count(finger_count):
    for action, count in GESTURES_MAPPING.items():
        if count == finger_count:
            return action
    return None

def get_display_info(action):
    return GESTURES_DISPLAY.get(action)