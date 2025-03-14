import cv2
import threading
import time
from ultralytics import YOLO

class HumanTracker:
    def __init__(self, camera_index=0, model_path="yolov8n.pt"):
        """
        Class for following a Human using Yolo
        """
        self.model = YOLO(model_path)  
        self.camera_index = camera_index
        self.running = False
        self.thread = None
        self.offset = 0  # silhouette offset from the middle
        self.direction = "silhouette in centre"  # correction direction
        self.max_offset = 200  # Maksymalny odchył od środka, skalowany do 100
        self.cap = cv2.VideoCapture(camera_index)

    def _process_frame(self):
        """
        Przetwarza obraz z kamery i aktualizuje dane.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            results = self.model(frame)
            frame_center = frame.shape[1] // 2  # Środek obrazu w osi X

            detected = False
            for result in results[0].boxes:
                cls = result.cls
                confidence = result.conf.item()
                x1, y1, x2, y2 = map(int, result.xyxy[0])  # Współrzędne prostokąta
                human_center = (x1 + x2) // 2  # Środek sylwetki w osi X

                if cls == 0 and confidence > 0.75:  # Detekcja człowieka
                    detected = True
                    self.offset = human_center - frame_center
                    break

            if not detected:
                self.offset = 0
                self.direction = "Brak sylwetki"

            time.sleep(0.01)  # Zapobiega przeciążeniu CPU

    def start(self):
        """Rozpoczyna śledzenie w nowym wątku."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._process_frame)
            self.thread.start()

    def stop(self):
        """Zatrzymuje wątek śledzenia."""
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()

    def get_offset(self):
        """Zwraca przesunięcie sylwetki względem środka obrazu."""
        return self.offset


    def __del__(self):
        """Czyszczenie zasobów."""
        self.cap.release()
        cv2.destroyAllWindows()


"""
# Testowanie klasy
if __name__ == "__main__":
    tracker = HumanTracker()
    tracker.start()

    try:
        while True:
            offset = tracker.get_offset()
            direction = tracker.get_direction()
            print(f"Offset: {offset}, Direction: {direction}")
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
"""