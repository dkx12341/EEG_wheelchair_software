import cv2
import threading
import time
from ultralytics import YOLO

class HumanTracker:
    def __init__(self, model_path='yolov8n.pt', camera_index=0):
        # Initialize YOLO model
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(camera_index)
        self.frame_center = None
        self.MAX_OFFSET = 100
        self.video = None


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
                print(offset)
        
        return image

    def start_detection(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = self.detect_human(frame)
           
            #cv2.imshow("Human Detection with YOLO", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    detector = HumanTracker()
    detector.start_detection()
