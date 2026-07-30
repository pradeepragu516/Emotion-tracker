class ContextMemory:
    def __init__(self):
        self.context = {
            "emotion_mode": None,
            "last_command": None,
            "user_profile": {}
        }

    def update_emotion(self, mood):
        self.context["emotion_mode"] = mood

    def update_user_profile(self, gender, age):
        self.context["user_profile"] = {"gender": gender, "age": age}

    def update_last_result(self, result):
        self.context["last_result"] = result

    def get_context(self):
        return self.context
