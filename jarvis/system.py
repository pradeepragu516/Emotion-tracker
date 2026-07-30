import os
import webbrowser
import datetime
import urllib.parse
import random
import ctypes

def change_volume(action_type):
    """
    Sends native Windows virtual key presses for volume control.
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP   = 0xAF
    """
    try:
        user32 = ctypes.windll.user32
        if action_type == "up":
            for _ in range(5):
                user32.keybd_event(0xAF, 0, 0, 0)
                user32.keybd_event(0xAF, 0, 2, 0)
        elif action_type == "down":
            for _ in range(5):
                user32.keybd_event(0xAE, 0, 0, 0)
                user32.keybd_event(0xAE, 0, 2, 0)
        elif action_type in ["mute", "unmute"]:
            user32.keybd_event(0xAD, 0, 0, 0)
            user32.keybd_event(0xAD, 0, 2, 0)
    except Exception as e:
        print(f"[SystemController] Volume error: {e}")

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('ullAvailExtendedVirtual', ctypes.c_ulonglong)
    ]

def get_system_diagnostics():
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        ram_used = stat.dwMemoryLoad
        return f"System operational. RAM usage is at {ram_used}%."
    except Exception:
        return "System core operational and monitoring environment."

class SystemController:
    def execute(self, step):
        action = step.get("action")

        if action == "CANCEL_SHUTDOWN":
            try:
                os.system("shutdown /a")
                return {"speech": "Shutdown sequence has been canceled."}
            except Exception as e:
                return {"speech": f"Could not cancel shutdown: {e}"}

        elif action == "SHUTDOWN":
            os.system("shutdown /s /t 60")
            return {"speech": "Initiating system shutdown sequence in 60 seconds. Say 'cancel shutdown' to abort."}

        elif action == "OPEN_APP":
            app = step.get("app", "").lower()
            if app == "chrome":
                os.system("start chrome")
                return {"speech": "Opening Google Chrome."}
            elif app == "edge":
                os.system("start msedge")
                return {"speech": "Opening Microsoft Edge."}
            elif app == "youtube":
                webbrowser.open("https://www.youtube.com")
                return {"speech": "Opening YouTube."}
            elif app == "spotify":
                os.system("start spotify:")
                return {"speech": "Opening Spotify."}
            elif app == "vscode":
                os.system("code .")
                return {"speech": "Opening Visual Studio Code."}
            elif app == "notepad":
                os.system("start notepad")
                return {"speech": "Opening Notepad."}
            elif app == "calculator":
                os.system("calc")
                return {"speech": "Opening Calculator."}
            elif app == "paint":
                os.system("start mspaint")
                return {"speech": "Opening Paint."}
            elif app == "cmd":
                os.system("start cmd")
                return {"speech": "Opening Command Prompt."}
            elif app == "explorer":
                os.system("start explorer")
                return {"speech": "Opening File Explorer."}
            elif app == "taskmgr":
                os.system("start taskmgr")
                return {"speech": "Opening Task Manager."}
            elif app == "settings":
                os.system("start ms-settings:")
                return {"speech": "Opening Windows Settings."}
            elif app == "camera":
                os.system("start microsoft.windows.camera:")
                return {"speech": "Opening Camera."}
            elif app in ["word", "excel", "powerpoint"]:
                os.system(f"start win{app}" if app == "word" else f"start {app}")
                return {"speech": f"Opening Microsoft {app.capitalize()}."}
            else:
                try:
                    os.system(f"start {app}")
                    return {"speech": f"Opening {app}."}
                except Exception:
                    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(app)}")
                    return {"speech": f"Searching for {app}."}

        elif action == "PLAY_YOUTUBE":
            query = step.get("query", "")
            if query:
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                webbrowser.open(url)
                return {"speech": f"Playing {query} on YouTube."}
            else:
                webbrowser.open("https://www.youtube.com")
                return {"speech": "Opening YouTube."}

        elif action == "PLAY_MUSIC":
            webbrowser.open("https://music.youtube.com")
            return {"speech": "Opening music stream."}

        elif action == "SEARCH_WEB":
            query = step.get("query", "Google")
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return {"speech": f"Searching Google for {query}."}

        elif action == "VOLUME_UP":
            change_volume("up")
            return {"speech": "Increasing volume."}

        elif action == "VOLUME_DOWN":
            change_volume("down")
            return {"speech": "Decreasing volume."}

        elif action == "MUTE":
            change_volume("mute")
            return {"speech": "Muting audio."}

        elif action == "UNMUTE":
            change_volume("unmute")
            return {"speech": "Unmuting audio."}

        elif action == "SET_VOLUME":
            val = step.get("value", 50)
            change_volume("up" if val > 50 else "down")
            return {"speech": f"Volume set to {val}%."}

        elif action == "GET_TIME":
            now_time = datetime.datetime.now().strftime("%I:%M %p")
            return {"speech": f"The current time is {now_time}."}

        elif action == "GET_DATE":
            now_date = datetime.datetime.now().strftime("%B %d, %Y")
            return {"speech": f"Today is {now_date}."}

        elif action == "SYSTEM_STATUS":
            diag = get_system_diagnostics()
            return {"speech": diag}

        elif action == "TELL_JOKE":
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why was the computer cold? Because it left its Windows open!",
                "An SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
                "Why do Java developers wear glasses? Because they don't C-sharp!"
            ]
            selected_joke = random.choice(jokes)
            return {"speech": selected_joke}

        elif action == "GREETING":
            return {"speech": "Hello! I am Jarvis, your emotion-aware assistant. How can I help you today?"}

        elif action == "SPEAK_RESPONSE":
            return {"speech": step.get("speech", "Standing by.")}

        elif action == "EMOTION_RESPONSE":
            return {"speech": "Remember, every day brings a fresh start. I am right here with you."}

        elif action == "IDLE":
            return {"speech": "Standing by."}

        return {"speech": f"Action {action} executed."}


