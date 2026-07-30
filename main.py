import cv2
import time
import numpy as np

from vision.face_detector import FaceDetector
from vision.emotion_detector import EmotionDetector
from vision.age_gender_detector import AgeGenderDetector
from vision.face_tracker import FaceTracker

from jarvis.core import JarvisCore
from jarvis.listener import listen_async
from jarvis.speaker import is_speaking


def draw_hud(frame, status_text, fps, detected_info=None):
    """
    Draws a modern HUD (Heads Up Display) overlay on the video frame.
    """
    h, w = frame.shape[:2]

    # --- Top Banner Panel ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), (15, 15, 25), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # System Status & Title
    cv2.putText(frame, "JARVIS AI – EMOTION AWARE ASSISTANT", (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 215, 0), 2)

    # Status Pill / Indicator
    if "LISTENING" in status_text:
        status_color = (0, 165, 255) # Orange
    elif is_speaking():
        status_color = (255, 0, 255) # Purple/Magenta
    else:
        status_color = (0, 255, 127) # Spring Green

    cv2.putText(frame, f"STATUS: {status_text}", (w - 260, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

    # FPS counter
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 75, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # --- Bottom Control Bar ---
    overlay_bot = frame.copy()
    cv2.rectangle(overlay_bot, (0, h - 35), (w, h), (15, 15, 25), -1)
    cv2.addWeighted(overlay_bot, 0.75, frame, 0.25, 0, frame)

    controls_str = "[V] Voice Command   |   [M] Toggle Detector   |   [Q] Quit"
    cv2.putText(frame, controls_str, (15, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)

    # --- Detected Target Panel ---
    if detected_info:
        gender, age, emotion, conf = detected_info
        panel_str = f"Target: {gender}, Age {age} | Mood: {emotion} ({conf:.0%})"
        cv2.putText(frame, panel_str, (15, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)


def draw_target_box(frame, x, y, w, h, label, color=(0, 255, 0)):
    """
    Draws stylized bounding box with corners and text badge.
    """
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    # Corner accents
    line_len = min(w, h) // 4
    cv2.line(frame, (x, y), (x + line_len, y), color, 3)
    cv2.line(frame, (x, y), (x, y + line_len), color, 3)

    cv2.line(frame, (x + w, y), (x + w - line_len, y), color, 3)
    cv2.line(frame, (x + w, y), (x + w, y + line_len), color, 3)

    # Text badge background
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
    cv2.rectangle(frame, (x, y - th - 12), (x + tw + 10, y), (20, 20, 20), -1)
    cv2.putText(frame, label, (x + 5, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)


def main():
    # =====================
    # INITIALIZATION
    # =====================
    print("[JARVIS] Initializing vision models & assistant core...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[JARVIS] Error: Could not access webcam (index 0). Trying camera index 1...")
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("[JARVIS] Fatal Error: No camera accessible.")
            return

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    current_detector_method = "haar"
    face_detector = FaceDetector(method=current_detector_method)
    emotion_detector = EmotionDetector("models/emotion_model.h5")
    age_gender_detector = AgeGenderDetector()

    face_tracker = FaceTracker(
        emotions_list=emotion_detector.emotions,
        gender_list=age_gender_detector.gender_list,
        age_list=age_gender_detector.age_list
    )

    jarvis = JarvisCore()

    last_emotion = None
    last_interaction_time = 0
    INTERACTION_COOLDOWN = 4.0  # seconds

    is_listening = False
    status_msg = "IDLE (READY)"
    last_recognized_cmd = ""

    def on_voice_command(recognized_text):
        nonlocal is_listening, status_msg, last_recognized_cmd
        if recognized_text:
            last_recognized_cmd = recognized_text
            status_msg = f"EXECUTING: '{recognized_text}'"
            plan = jarvis.think(recognized_text)
            results = jarvis.act(plan)
            jarvis.feedback(results)
        else:
            status_msg = "COMMAND NOT UNDERSTOOD"
        is_listening = False

    prev_frame_time = time.time()

    print("[JARVIS] System core initialized successfully. Press 'V' to speak, 'Q' to quit.")

    # =====================
    # MAIN LOOP
    # =====================
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        # Calculate FPS
        curr_frame_time = time.time()
        fps = 1.0 / max(0.001, (curr_frame_time - prev_frame_time))
        prev_frame_time = curr_frame_time

        # --- Face Detection ---
        faces = face_detector.detect_faces(frame)
        frame_detections = []

        h_img, w_img = frame.shape[:2]
        for (x, y, w, h, conf) in faces:
            x = max(0, x)
            y = max(0, y)
            w = min(w, w_img - x)
            h = min(h, h_img - y)

            face_roi = frame[y:y+h, x:x+w]
            if face_roi.size == 0:
                continue

            # Expanded crop for Age/Gender (includes hair & chin context)
            expanded_roi = AgeGenderDetector.get_expanded_crop(frame, (x, y, w, h), margin=0.20)

            # Predictions
            _, _, emo_probs = emotion_detector.predict_emotion(face_roi, return_probs=True)
            _, _, gender_probs, age_probs = age_gender_detector.predict(expanded_roi, return_probs=True)

            frame_detections.append(((x, y, w, h), emo_probs, gender_probs, age_probs, conf))

        # --- Face Tracking & Temporal Smoothing ---
        smoothed_results = face_tracker.process(frame_detections)
        detected_info = None

        for (bbox, sgender, sage, semo, econf, track_id) in smoothed_results:
            bx, by, bw, bh = bbox
            detected_info = (sgender, sage, semo, econf)

            # --- Emotion Perception Handling ---
            current_time = time.time()
            if semo != last_emotion and econf > 0.55:
                if current_time - last_interaction_time > INTERACTION_COOLDOWN:
                    jarvis.perceive(semo, sgender, sage)
                    last_emotion = semo
                    last_interaction_time = current_time

            # --- Render Target Box ---
            label = f"ID#{track_id}: {sgender}, {sage} | {semo} ({econf:.0%})"
            box_color = (0, 255, 0) if semo in ["Happy", "Neutral"] else (0, 165, 255)
            draw_target_box(frame, bx, by, bw, bh, label, color=box_color)

        # Update status message if idle
        if not is_listening and not is_speaking():
            if last_recognized_cmd:
                status_msg = f"LAST: {last_recognized_cmd}"
            else:
                status_msg = f"IDLE ({current_detector_method.upper()})"
        elif is_speaking():
            status_msg = "SPEAKING..."

        # Draw HUD Overlay
        draw_hud(frame, status_msg, fps, detected_info)

        cv2.imshow("JARVIS – Emotion Aware AI Assistant", frame)

        # =====================
        # KEYBOARD CONTROLS
        # =====================
        key = cv2.waitKey(1) & 0xFF

        if key == ord('v') or key == ord('V'):
            if not is_listening:
                is_listening = True
                status_msg = "LISTENING..."
                listen_async(on_voice_command, phrase_time_limit=5, timeout=4)

        elif key == ord('m') or key == ord('M'):
            # Toggle detection method
            current_detector_method = "mtcnn" if current_detector_method == "haar" else "haar"
            print(f"[JARVIS] Switching face detector to: {current_detector_method}")
            face_detector = FaceDetector(method=current_detector_method)

        elif key == ord('q') or key == ord('Q'):
            print("[JARVIS] Shutting down AI assistant core.")
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys
    if "--jarvis-only" in sys.argv or "--jarvis" in sys.argv:
        import run_jarvis
        run_jarvis.main()
    else:
        main()



