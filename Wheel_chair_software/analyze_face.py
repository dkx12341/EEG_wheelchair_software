import cv2
import mediapipe as mp
import threading
import time
import numpy as np
import time
import matplotlib.pyplot as plt

SPEAKING_THRESHOLD = 10  # Threshold distance between lips to detect speaking
SPEAKING_TIMEOUT = 0.5   # Time without mouth movement to stop considering speaking

TIME_SLEEP = 0.01  # Delay between loops to avoid overloading CPU

CALIBRATION_TIMEOUT = 5  # Timeout for gaze calibration

class FaceAnalyzer:


    def __init__(self, display, cameras):
        """
        Initializes the FaceAnalyzer for detecting gaze direction and speaking status.

        Parameters:
        - display: Boolean to control whether to display the video output for debugging.
        - cameras: List of camera objects to process.
        """
        
        self.display = display
        self.key_points = [{} for _ in cameras]
        self.running = False
        self.thread = None
        self.cameras = cameras
        self.num_cameras = len(cameras)

        self.center_values = [None] * self.num_cameras
        self.left_values = [None] * self.num_cameras
        self.right_values = [None] * self.num_cameras

        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils

        self.landmark_indices = {
            "right_eye_outer": 33,
            "left_eye_outer": 263,
            "nose": 1,
            "upper_lip": 13,
            "lower_lip": 14
        }

        self.speaking_timer = [0] * self.num_cameras
        self.is_speaking_status = [False] * self.num_cameras


        #video feed
        self.video = None

    def start(self):
        """Starts the camera processing in a new thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def stop(self):
        """Stops camera processing and joins the thread."""
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()

    def get_points(self):
        """Returns the current key points for all cameras."""
        return self.key_points

    def calculate_raw_gaze_value(self, cam_idx):
        """Calculates raw gaze direction based on distances between key points for a specific camera."""
        required_points = ["right_eye_outer", "left_eye_outer", "nose"]
        if not all(point in self.key_points[cam_idx] for point in required_points):
            return None

        right_eye = np.array(self.key_points[cam_idx]["right_eye_outer"])
        left_eye = np.array(self.key_points[cam_idx]["left_eye_outer"])
        nose = np.array(self.key_points[cam_idx]["nose"])

        distance_right = np.linalg.norm(nose - right_eye)
        distance_left = np.linalg.norm(nose - left_eye)

        return distance_right - distance_left

    def calibrate_center(self):
        """Calibrates the center gaze direction for all cameras."""
        for cam_idx in range(self.num_cameras):
            start_time = time.time()
            while True:
                value = self.calculate_raw_gaze_value(cam_idx)
                if value is not None:
                    self.center_values[cam_idx] = value
                    print(f"Center calibration for camera {cam_idx}: {value}")
                    break
                elif time.time() - start_time > CALIBRATION_TIMEOUT:
                    print(f"Timeout during center calibration for camera {cam_idx}")
                    break
                else:
                    time.sleep(0.1)

    def calibrate_left(self):
        """Calibrates the left gaze direction for all cameras."""
        for cam_idx in range(self.num_cameras):
            start_time = time.time()
            while True:
                value = self.calculate_raw_gaze_value(cam_idx)
                if value is not None:
                    self.left_values[cam_idx] = value
                    print(f"Left calibration for camera {cam_idx}: {value}")
                    break
                elif time.time() - start_time > CALIBRATION_TIMEOUT:
                    print(f"Timeout during left calibration for camera {cam_idx}")
                    break
                else:
                    time.sleep(0.1)

    def calibrate_right(self):
        """Calibrates the right gaze direction for all cameras."""
        for cam_idx in range(self.num_cameras):
            start_time = time.time()
            while True:
                value = self.calculate_raw_gaze_value(cam_idx)
                if value is not None:
                    self.right_values[cam_idx] = value
                    print(f"Right calibration for camera {cam_idx}: {value}")
                    break
                elif time.time() - start_time > CALIBRATION_TIMEOUT:
                    print(f"Timeout during right calibration for camera {cam_idx}")
                    break
                else:
                    time.sleep(0.1)

    def is_calibrated(self):
        """Checks if all cameras are calibrated for left, center, and right gaze values."""
        for cam_idx in range(self.num_cameras):
            if None in (self.left_values[cam_idx], self.center_values[cam_idx], self.right_values[cam_idx]):
                return False
        return True

    def get_normalized_gaze(self):
        """Returns normalized gaze values for all cameras in the range from -100 to 100."""
        normalized_gazes = []
        for cam_idx in range(self.num_cameras):
            raw_value = self.calculate_raw_gaze_value(cam_idx)
            if raw_value is None or None in (self.left_values[cam_idx], self.center_values[cam_idx], self.right_values[cam_idx]):
                normalized_gazes.append(None)
                continue

            if raw_value < self.center_values[cam_idx]:
                normalized = np.interp(raw_value, [self.right_values[cam_idx], self.center_values[cam_idx]], [100, 0])
            else:
                normalized = np.interp(raw_value, [self.center_values[cam_idx], self.left_values[cam_idx]], [0, -100])

            normalized = max(min(normalized, 100), -100)
            normalized_gazes.append(normalized)
        return normalized_gazes

    def is_speaking(self, cam_idx):
        """Checks if the person is speaking based on the mouth opening distance."""
        if "upper_lip" in self.key_points[cam_idx] and "lower_lip" in self.key_points[cam_idx]:
            upper_lip = np.array(self.key_points[cam_idx]["upper_lip"])
            lower_lip = np.array(self.key_points[cam_idx]["lower_lip"])
            mouth_distance = np.linalg.norm(upper_lip - lower_lip)

            if mouth_distance > SPEAKING_THRESHOLD:
                self.is_speaking_status[cam_idx] = True
                self.speaking_timer[cam_idx] = time.time()
            elif time.time() - self.speaking_timer[cam_idx] > SPEAKING_TIMEOUT:
                self.is_speaking_status[cam_idx] = False
        else:
            self.is_speaking_status[cam_idx] = False

        return self.is_speaking_status[cam_idx]

    def get_speaking_status(self):
        """Returns the speaking status for each camera."""
        return self.is_speaking_status

    def _run(self):
        """Main method for processing camera input and detecting key facial points."""
        with self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as face_mesh:
            while self.running:
                for cam_idx, camera in enumerate(self.cameras):
                    if camera is None or not camera.isOpened():
                        continue

                    ret, frame = camera.read()
                    if not ret:
                        continue

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_results = face_mesh.process(frame_rgb)
                    self.key_points[cam_idx].clear()

                    if face_results.multi_face_landmarks:
                        for face_landmarks in face_results.multi_face_landmarks:
                            for point_name, idx in self.landmark_indices.items():
                                x = int(face_landmarks.landmark[idx].x * frame.shape[1])
                                y = int(face_landmarks.landmark[idx].y * frame.shape[0])
                                self.key_points[cam_idx][point_name] = (x, y)
                                if self.display:
                                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                                    cv2.putText(
                                        frame,
                                        point_name,
                                        (x + 5, y + 5),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (0, 0, 255),
                                        1
                                    )

                            if self.display:
                                self.mp_drawing.draw_landmarks(
                                    image=frame,
                                    landmark_list=face_landmarks,
                                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                                        color=(0, 255, 0), thickness=1, circle_radius=1
                                    ),
                                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                        color=(0, 255, 0), thickness=1
                                    )
                                )

                    self.is_speaking(cam_idx)

                    if self.display:
                        speaking_text = "Speaking" if self.is_speaking_status[cam_idx] else "Not Speaking"
                        cv2.putText(frame, speaking_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                        cv2.imshow(f"Camera {cam_idx}", frame)
                        self.video = frame
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.stop()
                            break

                time.sleep(TIME_SLEEP)

            for cam in self.cameras:
                cam.release()
            cv2.destroyAllWindows()
