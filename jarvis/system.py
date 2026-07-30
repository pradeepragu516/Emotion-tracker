import os
import webbrowser
import datetime
import urllib.parse

class SystemController:
    def execute(self, step):
        action = step.get("action")

        if action == "OPEN_CHROME":
            try:
                os.system("start chrome")
                return {"speech": "Opening Google Chrome."}
            except Exception as e:
                webbrowser.open("https://www.google.com")
                return {"speech": "Opening web browser."}

        elif action == "OPEN_YOUTUBE":
            webbrowser.open("https://www.youtube.com")
            return {"speech": "Opening YouTube."}

        elif action == "SEARCH_WEB":
            query = step.get("query", "Google")
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return {"speech": f"Searching Google for {query}."}

        elif action == "OPEN_NOTEPAD":
            os.system("start notepad")
            return {"speech": "Opening Notepad."}

        elif action == "OPEN_CALCULATOR":
            os.system("calc")
            return {"speech": "Opening Calculator."}

        elif action == "GET_TIME":
            now_time = datetime.datetime.now().strftime("%I:%M %p")
            return {"speech": f"The current time is {now_time}."}

        elif action == "GET_DATE":
            now_date = datetime.datetime.now().strftime("%B %d, %Y")
            return {"speech": f"Today is {now_date}."}

        elif action == "SYSTEM_STATUS":
            return {"speech": "System core operational. Online and monitoring environment."}

        elif action == "PLAY_MUSIC":
            webbrowser.open("https://music.youtube.com")
            return {"speech": "Opening music stream."}

        elif action == "SHUTDOWN":
            # Note: 60 second delay to avoid accidental immediate shutdown
            os.system("shutdown /s /t 60")
            return {"speech": "Initiating system shutdown sequence in 60 seconds."}

        elif action == "SET_VOLUME":
            return {"speech": "Volume adjusted."}

        elif action == "SPEAK_RESPONSE":
            return {"speech": step.get("speech", "Standing by.")}

        elif action == "EMOTION_RESPONSE":
            return {"speech": "Remember, every day brings a fresh start. I am right here with you."}

        elif action == "IDLE":
            return {"speech": "Standing by."}

        return {"speech": f"Action {action} executed."}

