import threading
import queue
import pyttsx3

_speech_queue = queue.Queue()
_is_speaking_flag = False

def _tts_worker():
    global _is_speaking_flag
    engine = None
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
    except Exception as e:
        print(f"[Speaker] TTS engine init error: {e}")

    while True:
        text = _speech_queue.get()
        if text is None:
            break
        print(f"[JARVIS Speaking]: {text}")
        _is_speaking_flag = True
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[Speaker] Error during speech synthesis: {e}")
        _is_speaking_flag = False
        _speech_queue.task_done()

# Start background TTS thread as daemon
_worker_thread = threading.Thread(target=_tts_worker, daemon=True)
_worker_thread.start()

def speak(text):
    """
    Asynchronously enqueues text to be spoken without blocking the caller.
    """
    if text:
        _speech_queue.put(text)

def is_speaking():
    """
    Returns True if TTS is currently speaking or has items queued.
    """
    return _is_speaking_flag or not _speech_queue.empty()

