"""
SoulSync — Recommender (Multimodal)
recommender.py
"""

import random
import win32com.client

# ── Message bank ──────────────────────────────────────────────────────────────
MULTIMODAL_MESSAGES = {
    ("Slumped", "sigh"): [
        "Deep fatigue detected. Let's do a quick 30-second shoulder roll and take a deep breath.",
        "You seem really drained. Rest your eyes, roll your shoulders, and breathe slowly.",
    ],
    ("Slumped", "yawn"): [
        "Energy dip detected. It might be a good time to stand up and grab a glass of water.",
        "You are getting sleepy. Stand up, stretch your arms overhead, and take three deep breaths.",
    ],
    ("Slumped", "silence"): [
        "Your posture is dropping. Try sitting upright and rolling your neck gently.",
        "Fatigue signal detected. Consider standing up for 60 seconds and stretching your back.",
    ],
    ("Restless", "sigh"): [
        "You seem tense and frustrated. Try a 60-second breathing reset before continuing.",
        "Stress detected. Step away for a moment, shake out your hands, and breathe deeply.",
    ],
    ("Restless", "yawn"): [
        "Tired but restless. Your body needs a proper break. Try a 5-minute walk.",
        "You seem both tired and wired. A short walk outside would help reset your energy.",
    ],
    ("Restless", "silence"): [
        "You seem slightly tense. Try resetting your chair position and relaxing your shoulders.",
        "High movement detected. Try grounding yourself. Feet flat, back straight, hands on desk.",
        "Restlessness detected. Take three slow deep breaths and plant your feet flat on the floor.",
    ],
    ("Balanced", "sigh"): [
        "Good posture, but you sound a bit tired. A short break might help.",
    ],
    ("Balanced", "yawn"): [
        "Great posture! But a yawn detected. Maybe time for a short break or some water.",
    ],
    ("Balanced", "silence"): [
        "Great posture! Keep it up.",
        "You are sitting well. Stay focused.",
        "Excellent alignment. Well done.",
    ],
}

CONFIRMATION_COUNT = 3


class Recommender:
    def __init__(self):
        self._state_count = {}
        self._last_spoken = None

    def get_message(self, visual_state: str, audio_event: str = "silence"):
        # Track consecutive predictions
        if self._state_count.get("state") == visual_state:
            self._state_count["count"] = self._state_count.get("count", 0) + 1
        else:
            self._state_count = {"state": visual_state, "count": 1}

        if self._state_count["count"] < CONFIRMATION_COUNT:
            return None

        # Balanced + silence speaks only occasionally
        if visual_state == "Balanced" and audio_event == "silence":
            if random.random() > 0.2:
                return None

        # Look up combined key, fall back to silence
        messages = MULTIMODAL_MESSAGES.get((visual_state, audio_event))
        if not messages:
            messages = MULTIMODAL_MESSAGES.get((visual_state, "silence"), [])
        if not messages:
            return None

        # Avoid repeating last message
        choices = [m for m in messages if m != self._last_spoken]
        if not choices:
            choices = messages

        msg = random.choice(choices)
        self._last_spoken = msg
        return msg

    def speak(self, text: str):
        """Uses Windows native SAPI — reliable across all threads."""
        try:
            print(f"[SoulSync speaks]: {text}")
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        except Exception as e:
            print(f"[Recommender error]: {e}")