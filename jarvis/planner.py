from jarvis.intents import classify_intent

class TaskPlanner:
    def create_plan(self, command, context):
        intent, confidence, payload = classify_intent(command)

        if confidence < 0.5:
            return [{"action": "SEARCH_WEB", "query": command}]

        if intent == "CANCEL_SHUTDOWN":
            return [{"action": "CANCEL_SHUTDOWN"}]

        if intent == "SHUTDOWN":
            return [
                {"action": "SHUTDOWN"}
            ]

        if intent == "OPEN_APP":
            return [{"action": "OPEN_APP", "app": payload}]

        if intent == "OPEN_CHROME":
            return [{"action": "OPEN_APP", "app": "chrome"}]

        if intent == "OPEN_YOUTUBE":
            return [{"action": "OPEN_APP", "app": "youtube"}]

        if intent == "OPEN_NOTEPAD":
            return [{"action": "OPEN_APP", "app": "notepad"}]

        if intent == "OPEN_CALCULATOR":
            return [{"action": "OPEN_APP", "app": "calculator"}]

        if intent == "PLAY_YOUTUBE":
            return [{"action": "PLAY_YOUTUBE", "query": payload}]

        if intent == "PLAY_MUSIC":
            return [{"action": "PLAY_MUSIC"}]

        if intent == "SEARCH_WEB":
            return [{"action": "SEARCH_WEB", "query": payload}]

        if intent == "VOLUME_UP":
            return [{"action": "VOLUME_UP"}]

        if intent == "VOLUME_DOWN":
            return [{"action": "VOLUME_DOWN"}]

        if intent == "MUTE":
            return [{"action": "MUTE"}]

        if intent == "UNMUTE":
            return [{"action": "UNMUTE"}]

        if intent == "SET_VOLUME":
            return [{"action": "SET_VOLUME", "value": payload}]

        if intent == "GET_TIME":
            return [{"action": "GET_TIME"}]

        if intent == "GET_DATE":
            return [{"action": "GET_DATE"}]

        if intent == "SYSTEM_STATUS":
            return [{"action": "SYSTEM_STATUS"}]

        if intent == "TELL_JOKE":
            return [{"action": "TELL_JOKE"}]

        if intent == "GREETING":
            return [{"action": "GREETING", "text": payload}]

        if intent == "EMOTION_TALK":
            return [{"action": "EMOTION_RESPONSE"}]

        return [{"action": "SEARCH_WEB", "query": command}]


