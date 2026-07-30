class EmotionEngine:
    def __init__(self):
        self.responses = {
            "Happy": "You seem happy today. Shall we do something productive?",
            "Sad": "I sense sadness. I'm here with you. Do you want to talk?",
            "Angry": "Take a deep breath. I can help calm things down.",
            "Surprise": "That looks surprising. Something interesting?",
            "Fear": "Everything is under control. You are safe.",
            "Disgust": "I sense discomfort. Let me know how I can help.",
            "Neutral": "Awaiting your command."
        }

    def analyze(self, emotion):
        verbal_response = self.responses.get(emotion, "I'm observing your state.")
        return {"verbal_response": verbal_response}
