import cv2
import face_recognition
import os
import time

CURENT_TIME = 0.5 # czas jaki musi upłynąć od pierwszego zarejestrowania twarzy do kolejnego aby zrucić imie twarzy

class FaceRecognition:
    def __init__(self, faces_directory, display_video, camera):
        """
        Initializes the FaceRecognition class to detect if a visible face in the camera
        matches a stored face, returning the name of the person or 'unknown' if not found.

        Parameters:
        - faces_directory: Path to the directory containing subfolders, each named after
                           a person, with one or more face images in each.
        - display_video: Boolean to control whether to display the video feed (for debugging).
        - camera: The camera source from which frames will be captured.
        """
        self.known_faces = self.load_faces(faces_directory)
        if not self.known_faces:
            raise ValueError("No faces found in the provided directory.")
        self.display_video = display_video
        self.video_capture = camera

    def load_faces(self, faces_directory):
        """
        Loads face encodings from the provided directory.

        Parameters:
        - faces_directory: Path to the main directory containing subdirectories
                           named after each person, with their face images.

        Returns:
        - A dictionary with person names as keys and a list of their face encodings as values.
        """
        known_faces = {}
        for person_name in os.listdir(faces_directory):
            person_folder = os.path.join(faces_directory, person_name)
            if os.path.isdir(person_folder):
                encodings = []
                for image_file in os.listdir(person_folder):
                    image_path = os.path.join(person_folder, image_file)
                    encoding = self.find_face_encoding(image_path)
                    if encoding is not None:
                        encodings.append(encoding)
                if encodings:
                    known_faces[person_name] = encodings
        return known_faces

    def find_face_encoding(self, image_path):
        """
        Detects and encodes a face from an image file.

        Parameters:
        - image_path: Path to the image file containing a face.

        Returns:
        - The face encoding if a face is detected; otherwise, None.
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image from path {image_path}.")
            return None
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0]
        else:
            print(f"No face found in {image_path}")
            return None

    def wait_for_face(self):
        """
        Continuously checks the camera feed for faces. If a recognized face is stable (appears
        consistently for at least 0.5 seconds), returns the name of the person. Otherwise,
        returns 'unknown' if the face is unrecognized.

        Returns:
        - The name of the first stable recognized face or 'unknown' if unrecognized.
        """
        last_seen_times = {}

        try:
            while True:
                ret, frame = self.video_capture.read()
                if not ret:
                    break

                face_encodings = face_recognition.face_encodings(frame)
                face_locations = face_recognition.face_locations(frame)

                if not face_encodings:
                    if self.display_video:
                        cv2.imshow('Video', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue

                current_names = ["unknown"] * len(face_encodings)

                for i, face_encoding in enumerate(face_encodings):
                    for person_name, encodings in self.known_faces.items():
                        matches = face_recognition.compare_faces(encodings, face_encoding)
                        if True in matches:
                            current_names[i] = person_name
                            break

                current_time = time.time()
                for i, name in enumerate(current_names):
                    if name != "unknown":
                        if name in last_seen_times:
                            if current_time - last_seen_times[name] >= CURENT_TIME:
                                return name  # Return the name of the first stable recognized face
                        else:
                            last_seen_times[name] = current_time
                    elif "unknown" in current_names:  # If no recognized face found
                        return "unknown"  # Return 'unknown' for unrecognized face

                if self.display_video:
                    for (top, right, bottom, left), name in zip(face_locations, current_names):
                        color = (0, 255, 0) if name != "unknown" else (0, 0, 255)
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                    cv2.imshow('Video', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.video_capture.release()
            if self.display_video:
                cv2.destroyAllWindows()

        return "No stable face detected"

    def __del__(self):
        if self.video_capture.isOpened():
            self.video_capture.release()
