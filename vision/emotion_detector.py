import os
import cv2
import numpy as np

class EmotionDetector:
    def __init__(self, model_path="models/emotion_model.h5"):
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, model_path)

        self.model = None
        self.emotions = [
            'Angry', 'Disgust', 'Fear',
            'Happy', 'Sad', 'Surprise', 'Neutral'
        ]
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        if os.path.exists(model_path):
            try:
                from tensorflow.keras.models import load_model
                self.model = load_model(model_path, compile=False)
            except Exception as e:
                print(f"[EmotionDetector] Failed to load emotion model: {e}")
        else:
            print(f"[EmotionDetector] Model file not found at {model_path}")

    def predict_emotion(self, face_roi, return_probs=False):
        if self.model is None:
            default_probs = np.array([0.05, 0.05, 0.05, 0.1, 0.05, 0.05, 0.65], dtype=np.float32)
            if return_probs:
                return "Neutral", 0.65, default_probs
            return "Neutral", 0.65

        try:
            if face_roi is None or face_roi.size == 0:
                default_probs = np.zeros(7, dtype=np.float32)
                if return_probs:
                    return "Unknown", 0.0, default_probs
                return "Unknown", 0.0

            # Convert to grayscale if BGR
            if len(face_roi.shape) == 3 and face_roi.shape[2] == 3:
                gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_roi.copy()

            # Contrast equalization to reduce shadow / illumination noise
            gray = self.clahe.apply(gray)

            # Resize to 48x48
            face = cv2.resize(gray, (48, 48), interpolation=cv2.INTER_AREA)

            # Normalize
            face = face.astype("float32") / 255.0

            # Reshape to (1, 48, 48, 1)
            face = np.expand_dims(face, axis=0)
            face = np.expand_dims(face, axis=-1)

            # Fast direct tensor inference (avoids Keras iterator overhead)
            preds = self.model(face, training=False).numpy()
            probs = preds[0]
            idx = int(np.argmax(probs))
            conf = float(probs[idx])

            if return_probs:
                return self.emotions[idx], conf, probs

            return self.emotions[idx], conf

        except Exception as e:
            print("[EmotionDetector] Emotion prediction error:", e)
            default_probs = np.zeros(7, dtype=np.float32)
            if return_probs:
                return "Unknown", 0.0, default_probs
            return "Unknown", 0.0


