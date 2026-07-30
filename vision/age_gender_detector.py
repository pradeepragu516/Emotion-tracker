import os
import cv2
import numpy as np

class AgeGenderDetector:
    def __init__(self, models_dir="models/age_gender"):
        if not os.path.isabs(models_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(base_dir, models_dir)

        age_model = os.path.join(models_dir, "age_net.caffemodel")
        age_proto = os.path.join(models_dir, "age_deploy.prototxt")
        gender_model = os.path.join(models_dir, "gender_net.caffemodel")
        gender_proto = os.path.join(models_dir, "gender_deploy.prototxt")

        self.age_net = None
        self.gender_net = None

        self.age_list = ['(0-2)', '(4-6)', '(8-12)', '(15-20)',
                         '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.gender_list = ['Male', 'Female']
        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

        try:
            if os.path.exists(age_model) and os.path.exists(age_proto):
                self.age_net = cv2.dnn.readNet(age_model, age_proto)
            else:
                print(f"[AgeGenderDetector] Missing age model/proto in {models_dir}")

            if os.path.exists(gender_model) and os.path.exists(gender_proto):
                self.gender_net = cv2.dnn.readNet(gender_model, gender_proto)
            else:
                print(f"[AgeGenderDetector] Missing gender model/proto in {models_dir}")
        except Exception as e:
            print(f"[AgeGenderDetector] Initialization error: {e}")

    @staticmethod
    def get_expanded_crop(frame, bbox, margin=0.20):
        """
        Expands the face crop by margin percentage to capture full head/hair context.
        """
        h_img, w_img = frame.shape[:2]
        x, y, w, h = bbox

        dw = int(w * margin)
        dh = int(h * margin)

        x1 = max(0, x - dw)
        y1 = max(0, y - dh)
        x2 = min(w_img, x + w + dw)
        y2 = min(h_img, y + h + dh)

        crop = frame[y1:y2, x1:x2]
        return crop

    def predict(self, face_img, return_probs=False):
        if face_img is None or face_img.size == 0 or face_img.shape[0] < 10 or face_img.shape[1] < 10:
            if return_probs:
                return "Unknown", "Unknown", None, None
            return "Unknown", "Unknown"

        if self.gender_net is None or self.age_net is None:
            if return_probs:
                return "Unknown", "Unknown", None, None
            return "Unknown", "Unknown"

        try:
            blob = cv2.dnn.blobFromImage(
                face_img, 1.0, (227, 227),
                self.MODEL_MEAN_VALUES, swapRB=False
            )

            # Gender Prediction
            self.gender_net.setInput(blob)
            gender_preds = self.gender_net.forward()[0]
            gender_idx = int(gender_preds.argmax())
            gender = self.gender_list[gender_idx]

            # Age Prediction
            self.age_net.setInput(blob)
            age_preds = self.age_net.forward()[0]
            age_idx = int(age_preds.argmax())
            age = self.age_list[age_idx]

            if return_probs:
                return gender, age, gender_preds, age_preds

            return gender, age
        except Exception as e:
            print("[AgeGenderDetector] Prediction error:", e)
            if return_probs:
                return "Unknown", "Unknown", None, None
            return "Unknown", "Unknown"


