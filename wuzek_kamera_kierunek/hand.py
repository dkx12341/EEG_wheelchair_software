import cv2
import mediapipe as mp
import threading
import time
import numpy as np
import simpleaudio as sa  # Library for playing sounds

class HandSteeringAnalyzer:
    def __init__(self, display, cams):
        """Inicjalizuje klasę z opcją wyświetlania obrazu."""
        self.display = display  # Flaga boolean ustawiająca, czy obraz będzie wyświetlany
        self.hand_positions = [{} for _ in cams]  # Lista słowników dla kluczowych punktów ręki dla każdej kamery
        self.running = False  # Flaga do kontrolowania wątku
        self.thread = None  # Wątek do przetwarzania obrazów z kamer

        self.cameras = cams  # Lista obiektów VideoCapture
        self.num_cameras = len(cams)  # Liczba kamer

        # Wartości kalibracji dla każdej kamery
        self.center_values = [None] * self.num_cameras
        self.left_values = [None] * self.num_cameras
        self.right_values = [None] * self.num_cameras

        # Inicjalizacja MediaPipe Hands i narzędzi do rysowania
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Lock dla operacji bezpiecznych dla wątków
        self.lock = threading.Lock()

    def set_display(self, display: bool):
        """Ustawia, czy obraz powinien być wyświetlany."""
        self.display = display

    def start(self):
        """Uruchamia przetwarzanie kamer w nowym wątku."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def stop(self):
        """Zatrzymuje przetwarzanie kamer i wątek."""
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()

    def get_hand_positions(self):
        """Zwraca bieżące kluczowe pozycje dłoni dla wszystkich kamer."""
        with self.lock:
            return self.hand_positions.copy()

    def calculate_raw_steering_value(self, cam_idx):
        """Oblicza surową wartość kierowania na podstawie pozycji dłoni dla danej kamery."""
        with self.lock:
            hands = self.hand_positions[cam_idx]

            # Pobranie szerokości ramki obrazu
            frame_width = self.frame_sizes[cam_idx][0]
            center_x = frame_width / 2

            if not hands and len(hands) == 1 and len(hands) > 2:
                return None  # Brak wykrycia dłoni

            # Jeśli wykryto dwie dłonie
            elif len(hands) == 2:
                left_hand = hands.get('left_hand')
                right_hand = hands.get('right_hand')

                if left_hand and right_hand:
                    # Obliczenie punktu środkowego między dłońmi
                    left_y = left_hand['wrist'][1]
                    right_y = right_hand['wrist'][1]
                    value = right_y - left_y

                    # Obliczenie przesunięcia od środka
                    #offset = midpoint - center_x
                    return value
                else:
                    return None

    def calibrate_center(self):
        """Kalibruje pozycję środkową dla wszystkich kamer."""
        for cam_idx in range(self.num_cameras):
            # Czeka na dostępność kluczowych punktów dla każdej kamery
            start_time = time.time()
            timeout = 5  # sekundy
            while True:
                value = self.calculate_raw_steering_value(cam_idx)
                if value is not None:
                    self.center_values[cam_idx] = value
                    print(f"Kalibracja środka dla kamery {cam_idx}: {value}")
                    break
                elif time.time() - start_time > timeout:
                    print(f"Przekroczenie czasu podczas kalibracji środka kamery {cam_idx}")
                    break
                else:
                    time.sleep(0.1)

    def calibrate_left(self):
        """Kalibruje pozycję maksymalnie w lewo dla wszystkich kamer."""
        for cam_idx in range(self.num_cameras):
            start_time = time.time()
            timeout = 5  # sekundy
            while True:
                value = self.calculate_raw_steering_value(cam_idx)
                if value is not None:
                    self.left_values[cam_idx] = value
                    print(f"Kalibracja lewej pozycji dla kamery {cam_idx}: {value}")
                    break
                elif time.time() - start_time > timeout:
                    print(f"Przekroczenie czasu podczas kalibracji lewej pozycji kamery {cam_idx}")
                    break
                else:
                    time.sleep(0.1)

    def calibrate_right(self):
        """Kalibruje pozycję maksymalnie w prawo dla wszystkich kamer."""
        for cam_idx in range(self.num_cameras):
            start_time = time.time()
            timeout = 5  # sekundy
            while True:
                value = self.calculate_raw_steering_value(cam_idx)
                if value is not None:
                    self.right_values[cam_idx] = value
                    print(f"Kalibracja prawej pozycji dla kamery {cam_idx}: {value}")
                    break
                elif time.time() - start_time > timeout:
                    print(f"Przekroczenie czasu podczas kalibracji prawej pozycji kamery {cam_idx}")
                    break
                else:
                    time.sleep(0.1)

    def is_calibrated(self):
        """Sprawdza, czy wszystkie kamery są skalibrowane."""
        for cam_idx in range(self.num_cameras):
            if None in (self.left_values[cam_idx], self.center_values[cam_idx], self.right_values[cam_idx]):
                return False
        return True

    def get_normalized_steering(self):
        """Zwraca znormalizowane wartości kierowania dla wszystkich kamer w zakresie od -100 do 100."""
        normalized_steerings = []
        for cam_idx in range(self.num_cameras):
            raw_value = self.calculate_raw_steering_value(cam_idx)
            if (
                raw_value is None
                or None in (
                    self.left_values[cam_idx],
                    self.center_values[cam_idx],
                    self.right_values[cam_idx],
                )
            ):
                normalized_steerings.append(None)
                continue  # Brak danych kalibracyjnych lub punktów

            # Normalizacja wartości
            if raw_value < self.center_values[cam_idx]:
                # Kierowanie w lewo (wartości mniejsze od center_value)
                normalized = np.interp(
                    raw_value,
                    [self.left_values[cam_idx], self.center_values[cam_idx]],
                    [-100, 0],
                )
            else:
                # Kierowanie w prawo (wartości większe od center_value)
                normalized = np.interp(
                    raw_value,
                    [self.center_values[cam_idx], self.right_values[cam_idx]],
                    [0, 100],
                )

            # Ograniczenie wartości do zakresu [-100, 100]
            normalized = max(min(normalized, 100), -100)
            normalized_steerings.append(normalized)
        return normalized_steerings

    def _run(self):
        """Główna metoda przetwarzająca obrazy z kamer i wykrywająca kluczowe punkty dłoni."""
        self.frame_sizes = [None] * self.num_cameras  # Przechowywanie rozmiarów ramek dla każdej kamery
        with self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        ) as hands:
            while self.running:
                for cam_idx, camera in enumerate(self.cameras):
                    if camera is None or not camera.isOpened():
                        continue

                    ret, frame = camera.read()
                    if not ret:
                        continue

                    # Obracanie obrazu poziomo dla trybu selfie
                    frame = cv2.flip(frame, 1)

                    # Przechowywanie rozmiaru ramki
                    self.frame_sizes[cam_idx] = (frame.shape[1], frame.shape[0])

                    # Konwersja obrazu do RGB, wymagana przez MediaPipe
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    hand_results = hands.process(frame_rgb)

                    # Czyszczenie słownika kluczowych punktów przed nową ramką
                    with self.lock:
                        self.hand_positions[cam_idx].clear()

                    if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
                        for hand_landmarks, handedness in zip(
                            hand_results.multi_hand_landmarks, hand_results.multi_handedness
                        ):
                            # Ustalanie, czy ręka to lewa czy prawa
                            hand_label = handedness.classification[0].label.lower()
                            hand_dict = {}

                            # Ekstrakcja pozycji nadgarstka (punkt 0)
                            x = int(hand_landmarks.landmark[0].x * frame.shape[1])
                            y = int(hand_landmarks.landmark[0].y * frame.shape[0])
                            hand_dict["wrist"] = (x, y)

                            # Opcjonalnie, dodanie większej ilości kluczowych punktów

                            with self.lock:
                                self.hand_positions[cam_idx][hand_label + "_hand"] = hand_dict

                            if self.display:
                                # Rysowanie punktów dłoni na obrazie
                                self.mp_drawing.draw_landmarks(
                                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                                )

                                # Dodanie etykiety na obrazie
                                cv2.putText(
                                    frame,
                                    hand_label,
                                    (x - 20, y - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (255, 0, 0),
                                    2,
                                )

                    # Wyświetlanie obrazu, jeśli flaga display jest ustawiona na True
                    if self.display:
                        cv2.imshow(f"Camera {cam_idx}", frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            self.stop()
                            break

                # Opcjonalnie, dodanie małego opóźnienia
                time.sleep(0.01)

            # Zwolnienie zasobów dla wszystkich kamer i zamknięcie okien
            for cam in self.cameras:
                cam.release()
            cv2.destroyAllWindows()

# Funkcja obsługująca dźwięki podczas kalibracji
def play_sound(frequency, duration=1000):
    """Odtwarza sygnał dźwiękowy o określonej częstotliwości i czasie trwania (w milisekundach)."""
    fs = 44100  # Częstotliwość próbkowania
    t = np.linspace(0, duration / 1000, int(fs * duration / 1000), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = tone * (2 ** 15 - 1) / np.max(np.abs(tone))
    audio = audio.astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, fs)
    play_obj.wait_done()

# Przykład użycia:
# Dodanie listy kamer do HandSteeringAnalyzer
hand_analyzer = HandSteeringAnalyzer(True, [cv2.VideoCapture(0)])  # Przykład z jedną kamerą
hand_analyzer.start()

# Oczekiwanie na uruchomienie analizy
time.sleep(2)

# Kalibracja pozycji środkowej dla wszystkich kamer
print("Kalibracja: Trzymaj kierownicę w pozycji środkowej")
play_sound(440, 1000)  # Sygnał dźwiękowy o 440 Hz na 1 sekundę
time.sleep(1)
hand_analyzer.calibrate_center()
print("Zakończono kalibrację pozycji środkowej")

# Kalibracja pozycji lewej dla wszystkich kamer
print("Kalibracja: Skręć kierownicę maksymalnie w lewo")
play_sound(550, 1000)  # Sygnał dźwiękowy o 550 Hz na 1 sekundę
time.sleep(1)
hand_analyzer.calibrate_left()
print("Zakończono kalibrację pozycji lewej")

# Kalibracja pozycji prawej dla wszystkich kamer
print("Kalibracja: Skręć kierownicę maksymalnie w prawo")
play_sound(660, 1000)  # Sygnał dźwiękowy o 660 Hz na 1 sekundę
time.sleep(1)
hand_analyzer.calibrate_right()
print("Zakończono kalibrację pozycji prawej")
play_sound(660, 100)
time.sleep(0.2)
play_sound(660, 100)

# Testowanie znormalizowanej wartości kierowania
print("Rozpoczęcie testowania kąta kierowania")
for i in range(2000):
    time.sleep(0.1)
    normalized_steerings = hand_analyzer.get_normalized_steering()
    for cam_idx, normalized_steering in enumerate(normalized_steerings):
        if normalized_steering is not None:
            print(f"Kamera {cam_idx} - Znormalizowana wartość kierowania: {normalized_steering:.2f}")
            # Opcjonalnie, odtworzenie dźwięku na podstawie wartości normalized_steering
            # play_sound(550 + (2 * normalized_steering), 100)
        else:
            print(f"Kamera {cam_idx} - Nie można obliczyć kąta kierowania.")

hand_analyzer.stop()
