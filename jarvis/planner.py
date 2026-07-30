from jarvis.intents import classify_intent

class TaskPlanner:
    def create_plan(self, command, context):
        intent, confidence, payload = classify_intent(command)

        if confidence < 0.5:
            return [{"action": "SPEAK_RESPONSE", "speech": "I am not sure what you mean. Could you rephrase?"}]

        if intent == "SEARCH_WEB":
            return [
                {"action": "SEARCH_WEB", "query": payload}
            ]

        if intent == "OPEN_CHROME":
            return [
                {"action": "OPEN_CHROME"}
            ]

        if intent == "OPEN_YOUTUBE":
            return [
                {"action": "OPEN_YOUTUBE"}
            ]

        if intent == "OPEN_NOTEPAD":
            return [
                {"action": "OPEN_NOTEPAD"}
            ]

        if intent == "OPEN_CALCULATOR":
            return [
                {"action": "OPEN_CALCULATOR"}
            ]

        if intent == "GET_TIME":
            return [
                {"action": "GET_TIME"}
            ]

        if intent == "GET_DATE":
            return [
                {"action": "GET_DATE"}
            ]

        if intent == "SYSTEM_STATUS":
            return [
                {"action": "SYSTEM_STATUS"}
            ]

        if intent == "PLAY_MUSIC":
            return [
                {"action": "SET_VOLUME", "value": 50},
                {"action": "PLAY_MUSIC"}
            ]

        if intent == "SHUTDOWN":
            return [
                {"action": "CONFIRM_USER"},
                {"action": "SHUTDOWN"}
            ]

        if intent == "EMOTION_TALK":
            return [
                {"action": "EMOTION_RESPONSE"}
            ]

        return [{"action": "IDLE"}]

