import sys
import time
from jarvis.core import JarvisCore
from jarvis.listener import listen
from jarvis.speaker import speak

def main():
    print("=" * 60)
    print("        JARVIS AI ASSISTANT – VOICE & COMMAND MODE        ")
    print("=" * 60)
    print("• Press [ENTER] to start voice listening via microphone.")
    print("• Or TYPE any command directly (e.g. 'open chrome', 'time', 'search python').")
    print("• Type 'exit' or press Ctrl+C to quit.\n")

    jarvis = JarvisCore()
    speak("Jarvis is online and ready for your command.")

    while True:
        try:
            print("\n------------------------------------------------------------")
            print("[JARVIS READY] Press [ENTER] to Speak OR Type Command: ", end="", flush=True)
            user_input = input().strip()

            if user_input.lower() in ["exit", "quit", "q", "stop"]:
                speak("Goodbye!")
                print("[JARVIS] Shutting down assistant core.")
                break

            if user_input:
                # User typed a text command
                command = user_input
            else:
                # User pressed Enter to trigger voice listening
                print("[JARVIS] Microphone active. Speak clearly now...")
                command = listen(phrase_time_limit=6, timeout=6)

            if not command:
                continue

            if command.lower() in ["exit", "quit", "stop", "bye"]:
                speak("Goodbye!")
                print("[JARVIS] Shutting down assistant core.")
                break

            # Execute plan & give feedback
            plan = jarvis.think(command)
            results = jarvis.act(plan)
            jarvis.feedback(results)
            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[JARVIS] Interrupted. Shutting down.")
            speak("Powering down.")
            break
        except Exception as e:
            print(f"[JARVIS] Unexpected error: {e}")

if __name__ == "__main__":
    main()

