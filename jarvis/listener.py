import threading
import speech_recognition as sr

# Shared recognizer instance
_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True
_recognizer.dynamic_energy_adjustment_damping = 0.15
_recognizer.pause_threshold = 0.8

def check_pyaudio():
    try:
        import pyaudio
        return True, "PyAudio installed."
    except ImportError:
        return False, "PyAudio is not installed in current Python environment. Run: .\\venv\\Scripts\\python.exe -m pip install pyaudio"

def listen(phrase_time_limit=6, timeout=6):
    """
    Synchronously listens for voice input and returns recognized text.
    """
    has_pyaudio, msg = check_pyaudio()
    if not has_pyaudio:
        print(f"[JARVIS] {msg}")
        return None

    try:
        with sr.Microphone() as source:
            print("[JARVIS] Microphone active. Listening now...")
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)

            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("[JARVIS] Processing recognition...")
            text = _recognizer.recognize_google(audio)
            text_str = text.strip().lower()
            print(f"[JARVIS] Recognized: '{text_str}'")
            return text_str

    except sr.UnknownValueError:
        print("[JARVIS] Speech not understood. Try speaking louder or closer to mic.")
        return None
    except sr.RequestError as e:
        print(f"[JARVIS] Google Speech API request error: {e}")
        return None
    except sr.WaitTimeoutError:
        print("[JARVIS] Listening timed out (no audio heard).")
        return None
    except OSError as e:
        print(f"[JARVIS] Microphone device access error (is another app using mic?): {e}")
        return None
    except Exception as e:
        print(f"[JARVIS] Audio error: {e}")
        return None

def listen_async(callback, phrase_time_limit=6, timeout=6):
    """
    Listens asynchronously in a background thread and invokes callback(text) when finished.
    """
    def _worker():
        result = listen(phrase_time_limit=phrase_time_limit, timeout=timeout)
        if callback:
            callback(result)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t



