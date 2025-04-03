
import torch  # Import PyTorch - używany do operacji z modelami YOLO
import cv2  # Import OpenCV - biblioteka do obsługi obrazów i wideo
from ultralytics import YOLO  # Import YOLO z biblioteki ultralytics

# Inicjalizacja modelu YOLO
# 'yolov8n.pt' to plik modelu YOLO w wersji nano (kompromis pomiędzy dokładnością a szybkością)
model = YOLO('yolov8n.pt')


def scale_offset(offset, frame_width):
    
    return ((offset / frame_width) * 100)

# Funkcja detect_human - przetwarza obraz i wykrywa sylwetki ludzi
def detect_human(image):
    # Wykonanie detekcji na obrazie przy użyciu modelu YOLO
    results = model(image)
    frame_center = image.shape[1] // 2
    max_offset = 200

    for result in results[0].boxes:
        cls = result.cls
        confidence = result.conf.item()
        x1, y1, x2, y2 = map(int, result.xyxy[0])

        x, y, w, h  = map(int, result.xywh[0])

        human_center = (x1 + x2) // 2
        human_height = (h)
        human_height_2 = y2 - y1
        human_width = (w)
        bottom_corner = (y1)
        # 0,0 at left upper corner
        # y2 is lower corner, y1 is higher



        if cls == 0 and confidence > 0.75:
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(image, f"Human: {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            offset = human_center - frame_center
            offset = scale_offset(offset, image.shape[0])
            print(offset)
            #direction = "Skręć w lewo -" if offset < 0 else "Skręć w prawo +" if offset > 0 else "Sylwetka w centrum"
            adjustment = abs(offset)
            adjustment_scaled = min(int((adjustment / max_offset) * 100), 100)
            #adjustment_message = f"{direction}{adjustment_scaled}px" if adjustment_scaled > 0 else "Sylwetka w centrum"
            #print(str(human_height) +" " + str(human_height_2))

    return image

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = detect_human(frame)
    cv2.imshow("Human Detection with YOLO", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
