import cv2

class FaceDetector:
    def __init__(self, method="haar"):
        self.method = method.lower()
        self.haar_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.mtcnn_detector = None
        if self.method == "mtcnn":
            try:
                from mtcnn import MTCNN
                self.mtcnn_detector = MTCNN()
            except Exception as e:
                print(f"[FaceDetector] MTCNN initialization warning: {e}. Falling back to Haar Cascade.")
                self.method = "haar"

    def detect_faces(self, frame):
        if frame is None or frame.size == 0:
            return []

        h_img, w_img = frame.shape[:2]
        if h_img < 60 or w_img < 60:
            return []

        faces = []
        try:
            if self.method == "mtcnn" and self.mtcnn_detector is not None:
                # Downscale frame for MTCNN performance if needed
                scale = 0.5
                small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
                rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                results = self.mtcnn_detector.detect_faces(rgb)

                for res in results:
                    x, y, w, h = res['box']
                    conf = res['confidence']

                    if conf < 0.85:
                        continue

                    # Upscale coordinates back to original frame size
                    x = int(x / scale)
                    y = int(y / scale)
                    w = int(w / scale)
                    h = int(h / scale)

                    # Clamp coordinates
                    x = max(0, x)
                    y = max(0, y)
                    w = min(w, w_img - x)
                    h = min(h, h_img - y)

                    if w > 20 and h > 20:
                        faces.append((x, y, w, h, float(conf)))
            else:
                # High performance Haar Cascade detector (~60+ FPS)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detected = self.haar_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

                for (x, y, w, h) in detected:
                    x = max(0, int(x))
                    y = max(0, int(y))
                    w = min(int(w), w_img - x)
                    h = min(int(h), h_img - y)

                    if w > 20 and h > 20:
                        faces.append((x, y, w, h, 0.95))

            return faces

        except Exception as e:
            print("[FaceDetector] Error detecting faces:", e)
            return []

