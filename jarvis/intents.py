def classify_intent(text):
    if not text:
        return ("UNKNOWN", 0.0, None)

    text = text.lower().strip()

    # Web search intents
    for prefix in ["search google for ", "search for ", "google ", "search ", "find "]:
        if text.startswith(prefix):
            query = text.replace(prefix, "").strip()
            if query:
                return ("SEARCH_WEB", 0.95, query)

    # App launches
    if "youtube" in text or "video" in text:
        return ("OPEN_YOUTUBE", 0.95, text)

    if "chrome" in text or "browser" in text or "google" in text:
        return ("OPEN_CHROME", 0.95, None)

    if "notepad" in text or "notes" in text or "text editor" in text:
        return ("OPEN_NOTEPAD", 0.95, None)

    if "calculator" in text or "calc" in text:
        return ("OPEN_CALCULATOR", 0.95, None)

    # Time and Date
    if any(w in text for w in ["time", "clock", "hour"]):
        return ("GET_TIME", 0.95, None)

    if any(w in text for w in ["date", "day", "today"]):
        return ("GET_DATE", 0.95, None)

    # System Status & Diagnostics
    if any(w in text for w in ["system", "status", "battery", "cpu", "ram"]):
        return ("SYSTEM_STATUS", 0.90, None)

    # Music & Entertainment
    if any(w in text for w in ["music", "song", "play", "audio"]):
        return ("PLAY_MUSIC", 0.90, None)

    # Shutdown
    if any(w in text for w in ["shutdown", "turn off", "power off"]):
        return ("SHUTDOWN", 0.99, None)

    # Conversation / Emotion talk
    if any(w in text for w in ["cheer", "sad", "happy", "depressed", "bored", "talk", "hello", "hi", "hey"]):
        return ("EMOTION_TALK", 0.90, None)

    return ("UNKNOWN", 0.4, text)


