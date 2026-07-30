import numpy as np
from collections import deque

def compute_iou(boxA, boxB):
    """
    Computes Intersection over Union (IoU) between two bounding boxes (x, y, w, h).
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou


class TrackedFace:
    def __init__(self, track_id, bbox, emo_probs, gender_probs, age_probs, emotions_list, gender_list, age_list):
        self.track_id = track_id
        self.bbox = bbox
        self.emotions_list = emotions_list
        self.gender_list = gender_list
        self.age_list = age_list

        buffer_len = 7
        self.emo_history = deque(maxlen=buffer_len)
        self.gender_history = deque(maxlen=buffer_len)
        self.age_history = deque(maxlen=buffer_len)

        self.missing_frames = 0
        self.update_preds(bbox, emo_probs, gender_probs, age_probs)

    def update_preds(self, bbox, emo_probs, gender_probs, age_probs):
        self.bbox = bbox
        self.missing_frames = 0

        if emo_probs is not None:
            self.emo_history.append(emo_probs)
        if gender_probs is not None:
            self.gender_history.append(gender_probs)
        if age_probs is not None:
            self.age_history.append(age_probs)

    def get_smoothed_predictions(self):
        """
        Calculates temporally smoothed predictions averaged over recent frames.
        """
        # Emotion
        if self.emo_history:
            mean_emo_probs = np.mean(self.emo_history, axis=0)
            emo_idx = int(np.argmax(mean_emo_probs))
            smoothed_emo = self.emotions_list[emo_idx]
            emo_conf = float(mean_emo_probs[emo_idx])
        else:
            smoothed_emo, emo_conf = "Neutral", 0.60

        # Gender
        if self.gender_history:
            mean_gender_probs = np.mean(self.gender_history, axis=0)
            gender_idx = int(np.argmax(mean_gender_probs))
            smoothed_gender = self.gender_list[gender_idx]
        else:
            smoothed_gender = "Unknown"

        # Age
        if self.age_history:
            mean_age_probs = np.mean(self.age_history, axis=0)
            age_idx = int(np.argmax(mean_age_probs))
            smoothed_age = self.age_list[age_idx]
        else:
            smoothed_age = "Unknown"

        return smoothed_gender, smoothed_age, smoothed_emo, emo_conf


class FaceTracker:
    def __init__(self, emotions_list, gender_list, age_list, iou_threshold=0.35):
        self.next_id = 1
        self.tracks = []
        self.iou_threshold = iou_threshold

        self.emotions_list = emotions_list
        self.gender_list = gender_list
        self.age_list = age_list

    def process(self, detections):
        """
        Detections: list of tuples (bbox, emo_probs, gender_probs, age_probs, face_conf)
        Returns: list of tuples (bbox, smoothed_gender, smoothed_age, smoothed_emo, emo_conf, track_id)
        """
        unmatched_detections = list(range(len(detections)))
        assigned_track_ids = set()

        # Match existing tracks to new detections using IoU
        for track in self.tracks:
            best_iou = 0.0
            best_det_idx = -1

            for det_idx in unmatched_detections:
                bbox, _, _, _, _ = detections[det_idx]
                iou_val = compute_iou(track.bbox, bbox)
                if iou_val > best_iou:
                    best_iou = iou_val
                    best_det_idx = det_idx

            if best_iou >= self.iou_threshold and best_det_idx != -1:
                bbox, emo_probs, gender_probs, age_probs, _ = detections[best_det_idx]
                track.update_preds(bbox, emo_probs, gender_probs, age_probs)
                unmatched_detections.remove(best_det_idx)
                assigned_track_ids.add(track.track_id)
            else:
                track.missing_frames += 1

        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            bbox, emo_probs, gender_probs, age_probs, _ = detections[det_idx]
            new_track = TrackedFace(
                self.next_id, bbox, emo_probs, gender_probs, age_probs,
                self.emotions_list, self.gender_list, self.age_list
            )
            self.next_id += 1
            self.tracks.append(new_track)

        # Remove dead tracks missing for more than 10 frames
        self.tracks = [t for t in self.tracks if t.missing_frames < 10]

        # Gather smoothed output results
        results = []
        for track in self.tracks:
            if track.missing_frames == 0:
                sgender, sage, semo, econf = track.get_smoothed_predictions()
                results.append((track.bbox, sgender, sage, semo, econf, track.track_id))

        return results
