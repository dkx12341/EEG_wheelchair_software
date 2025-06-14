import cv2
import threading
from ultralytics import YOLO

class HumanTracker:
    def __init__(self, model_path='yolov8n.pt', camera_index=0):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(camera_index)
        self.running = False
        self.thread = None
        self.frame_center = None
        self.MAX_OFFSET = 100
        self.video = None
        self.turn = 0

    def scale_offset(self, offset, frame_width):
        return (offset / frame_width) * self.MAX_OFFSET

    def detect_human(self, image):
        results = self.model(image)
        self.frame_center = image.shape[1] // 2

        for result in results[0].boxes:
            cls = result.cls
            confidence = result.conf.item()
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            human_center = (x1 + x2) // 2

            if cls == 0 and confidence > 0.75:
                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(image, f"Human: {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                offset = human_center - self.frame_center
                offset = self.scale_offset(offset, image.shape[0])
                self.video = image
                self.turn = int(offset)
                print(offset)

        return image

    def _run(self):
        """Private method to run detection loop in a thread."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = self.detect_human(frame)
            self.video = frame
            # Optionally show frame for debug
            # cv2.imshow("Human Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def start_detection(self):
        """Starts the detection thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def stop(self):
        """Stops detection and joins the thread."""
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()

# Example usage
if __name__ == "__main__":
    detector = HumanTracker()
    detector.start_detection()
