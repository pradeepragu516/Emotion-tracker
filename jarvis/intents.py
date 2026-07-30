import re

def clean_preambles(text):
    """
    Strips common wake words, greetings, and polite preambles from user input.
    """
    if not text:
        return ""
    text = text.lower().strip()
    
    # Remove leading wake words and polite phrases
    patterns = [
        r"^(hey\s+jarvis|ok\s+jarvis|hello\s+jarvis|hi\s+jarvis|jarvis)\b[\s,]*",
        r"^(please|could\s+you\s+please|can\s+you\s+please|could\s+you|can\s+you|would\s+you)\b[\s,]*",
        r"^(assistant|computer|bot)\b[\s,]*"
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "", text).strip()
    
    # Run once more in case preamble was combined (e.g. "hey jarvis please open...")
    for pattern in patterns:
        text = re.sub(pattern, "", text).strip()
        
    return text


def classify_intent(raw_text):
    if not raw_text:
        return ("UNKNOWN", 0.0, None)

    text = clean_preambles(raw_text)
    if not text:
        return ("UNKNOWN", 0.0, None)

    # 1. CANCEL SHUTDOWN (Must take priority over SHUTDOWN)
    if any(phrase in text for phrase in ["cancel shutdown", "abort shutdown", "stop shutdown", "don't shutdown", "dont shutdown", "nevermind shutdown"]):
        return ("CANCEL_SHUTDOWN", 0.99, None)

    # 2. SHUTDOWN
    if any(w in text for w in ["shutdown", "turn off computer", "power off computer", "turn off the PC", "shutdown pc"]):
        return ("SHUTDOWN", 0.99, None)

    # 3. VOLUME CONTROL
    if any(phrase in text for phrase in ["volume up", "increase volume", "louder", "turn volume up", "turn it up"]):
        return ("VOLUME_UP", 0.95, None)

    if any(phrase in text for phrase in ["volume down", "decrease volume", "lower volume", "quieter", "turn volume down", "turn it down"]):
        return ("VOLUME_DOWN", 0.95, None)

    if "unmute" in text:
        return ("UNMUTE", 0.95, None)

    if "mute" in text or "silence" in text:
        return ("MUTE", 0.95, None)

    volume_match = re.search(r"set volume to (\d+)", text)
    if volume_match:
        val = int(volume_match.group(1))
        return ("SET_VOLUME", 0.95, val)

    # 4. YOUTUBE PLAYBACK & SEARCH
    if "youtube" in text or text.startswith("play "):
        # Check if query is specified
        query = text
        for prefix in ["search youtube for ", "play on youtube ", "youtube search ", "play "]:
            if query.startswith(prefix):
                query = query.replace(prefix, "").strip()
        query = re.sub(r"\s+on youtube$", "", query).strip()
        
        if query and query not in ["youtube", "video", "music"]:
            return ("PLAY_YOUTUBE", 0.95, query)
        elif "youtube" in text:
            return ("OPEN_APP", 0.95, "youtube")

    # 5. JOKES
    if any(phrase in text for phrase in ["tell me a joke", "say a joke", "make me laugh", "tell a joke", "joke"]):
        return ("TELL_JOKE", 0.95, None)

    # 6. APP LAUNCHES
    apps_dict = {
        "google chrome": "chrome",
        "chrome": "chrome",
        "browser": "chrome",
        "microsoft edge": "edge",
        "edge": "edge",
        "spotify": "spotify",
        "vs code": "vscode",
        "vscode": "vscode",
        "code editor": "vscode",
        "notepad": "notepad",
        "notes": "notepad",
        "text editor": "notepad",
        "calculator": "calculator",
        "calc": "calculator",
        "paint": "paint",
        "mspaint": "paint",
        "drawing": "paint",
        "command prompt": "cmd",
        "cmd": "cmd",
        "terminal": "cmd",
        "powershell": "cmd",
        "file explorer": "explorer",
        "explorer": "explorer",
        "my computer": "explorer",
        "this pc": "explorer",
        "task manager": "taskmgr",
        "taskmgr": "taskmgr",
        "settings": "settings",
        "control panel": "settings",
        "camera": "camera",
        "webcam": "camera",
        "word": "word",
        "excel": "excel",
        "powerpoint": "powerpoint"
    }

    # Direct "open <app>" check
    if text.startswith("open ") or text.startswith("launch ") or text.startswith("start "):
        target_app = re.sub(r"^(open|launch|start)\s+", "", text).strip()
        if target_app in apps_dict:
            return ("OPEN_APP", 0.95, apps_dict[target_app])
        # Check partial match in apps_dict keys
        for app_name, app_key in apps_dict.items():
            if app_name in target_app:
                return ("OPEN_APP", 0.95, app_key)

    # Check if text explicitly contains an app keyword
    for app_name, app_key in apps_dict.items():
        if f"open {app_name}" in text or f"launch {app_name}" in text:
            return ("OPEN_APP", 0.95, app_key)

    # 7. TIME AND DATE
    if any(w in text for w in ["what time", "current time", "clock", "tell me the time"]):
        return ("GET_TIME", 0.95, None)
    if "time" in text and not any(w in text for w in ["weather", "search", "google"]):
        return ("GET_TIME", 0.95, None)

    if any(w in text for w in ["what date", "today's date", "current date", "what day is it"]):
        return ("GET_DATE", 0.95, None)
    if "date" in text:
        return ("GET_DATE", 0.95, None)

    # 8. SYSTEM STATUS
    if any(w in text for w in ["system status", "system info", "cpu", "ram", "battery", "performance", "system diagnostics"]):
        return ("SYSTEM_STATUS", 0.90, None)

    # 9. WEB SEARCH & QUESTIONS
    search_prefixes = [
        "search google for ", "search for ", "google ", "search ", "find ",
        "look up ", "browse ", "what is ", "who is ", "where is ", "how to ",
        "why is ", "why ", "tell me about ", "weather in ", "weather for ", "weather "
    ]
    for prefix in search_prefixes:
        if text.startswith(prefix):
            query = text.replace(prefix, "").strip()
            if query:
                return ("SEARCH_WEB", 0.95, text if prefix in ["weather in ", "weather for ", "weather ", "what is ", "who is ", "where is ", "how to ", "why "] else query)

    # 10. GREETINGS & SMALL TALK
    if any(w in text for w in ["hello", "hi", "hey", "good morning", "good evening", "how are you"]):
        return ("GREETING", 0.90, text)

    if any(w in text for w in ["cheer", "sad", "happy", "depressed", "bored", "lonely"]):
        return ("EMOTION_TALK", 0.90, text)

    # 11. DEFAULT FALLBACK TO WEB SEARCH
    # If the user asks or says anything non-trivial, route to Web Search instead of failing!
    return ("SEARCH_WEB", 0.70, text)



