import time
import cv2
import numpy as np
import sounddevice as sd
import time
import threading
import sys
import os
import keyboard
import pygame
import platform

from analyze_face import FaceAnalyzer  # Import klasy FaceAnalyzer
from recognize_speech import RealTimeRecognizer  # Import klasy RealTimeRecognizer
from recognize_face import Recognize_face
#from hand import HandSteeringAnalyzer
from speak import AudioPlayer
from chair_connection import ChairConnect
from EEG_manager import EEG_manager
from silhuette_tracking import HumanTracker


base_dir = os.path.dirname(os.path.realpath(__file__))

AUDIO_PATH = os.path.join(base_dir, 'voice')
FACE_PATH= os.path.join(base_dir, 'face')

VIDEO_FACE_COMPARE = False

active_thread = None
stop_thread_event = threading.Event()


audio_player = AudioPlayer(AUDIO_PATH)

def start_new_thread(function, *args):
    """
    Uruchamia nowy wątek z podaną funkcją, przerywając wcześniejszy wątek.
    """
    global active_thread, stop_thread_event

    # Przerwij aktywny wątek, jeśli istnieje
    if active_thread and active_thread.is_alive():
        stop_thread_event.set()
        active_thread.join()

    # Resetuj event zatrzymania
    stop_thread_event.clear()

    # Uruchom nowy wątek
    active_thread = threading.Thread(target=function, args=args)
    active_thread.start()



def beep(frequency, duration, samplerate=22050):
    """
    Generuje dźwięk o zadanej częstotliwości (Hz) i długości trwania (sekundy).
    """
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(wave, samplerate=samplerate, blocksize=1024, latency='high')
    sd.wait()


def find_know_face():
    camera = cv2.VideoCapture(0)  # Pierwsza dostępna kamera
    face_recognition_system = Recognize_face(FACE_PATH, VIDEO_FACE_COMPARE, camera)
    name = face_recognition_system.wait_for_face()
    face_recognition_system.video_capture.release()  # Zwolnij kamerę jawnie po zakończeniu
    cv2.destroyAllWindows()  # Zamknij wszystkie okna
    del face_recognition_system

    # Upewnij się, że kamera została zwolniona
    while camera.isOpened():
        camera.release()
        time.sleep(0.1)

    return name

def tell_hello(player, name):
    #print(name)
    player.play_audio("przywitanie", name)
    #time.sleep(2)

def tell_help_you(player):
    player.play_audio("pytanie_pomoc", "w_czym_mogę_pomóc")

def tell_end(player):
    player.play_audio("koniec", "wilhelm")

def kalibracja(player, face_ana):
    # Kalibracja pozycji środkowej dla wszystkich kamer
    player.play_audio("kalibracja", "przud")
    time.sleep(1)
    face_ana.calibrate_center()
    player.play_audio("kalibracja", "lewo")
    time.sleep(1)
    face_ana.calibrate_left()
    player.play_audio("kalibracja", "prawo")
    time.sleep(1)
    face_ana.calibrate_right()
    player.play_audio("kalibracja", "zakończono")

def test_wuzka():
    i = 0
    step = 100
    while not stop_thread_event.is_set():
        if i > 300:
            step = -100
        if i < 300:
            step = 100

        i += step
        wuzek.set_speed(i)
        time.sleep(1)


def ustaw_na():
    while not stop_thread_event.is_set():
        wuzek.set_speed(100)
        time.sleep(1)

def sterowanie_głową():
    """
    Funkcja obsługująca sterowanie głową.
    Pobiera wartości spojrzenia z `face_analyzer` i steruje wózkiem.
    """
    if not face_analyzer.is_calibrated():
        print("Kamera nie jest skalibrowana. Upewnij się, że wykonano kalibrację.")
        return

    wuzek.set_speed(100)  # Ustaw prędkość wózka
    print("Sterowanie głową aktywne.")

    while not stop_thread_event.is_set():
        # Pobierz wartości spojrzenia z face_analyzer
        normalized_gaze = face_analyzer.get_normalized_gaze()

        if normalized_gaze is None or normalized_gaze[0] is None:
            print("Nie można odczytać spojrzenia. Upewnij się, że kamera działa poprawnie.")
            time.sleep(0.1)
            continue

        # Ogranicz i zaokrąglij wartość sterowania (np. -100 do 100)
        ster_value = max(min(int(normalized_gaze[0]), 100), -100)
        print(f"Sterowanie: {ster_value}")  # Debugging wartości sterowania

        # Steruj wózkiem
        #
        #ster_value *= 10
        wuzek.set_steer(ster_value)

        # Opóźnienie dla płynniejszego działania
        time.sleep(0.05)

    print("Sterowanie głową zakończone.")



def sterowanie_eeg():
    
    print("Sterowanie eeg aktywne.")

    EEG_obj = EEG_manager()

    while not stop_thread_event.is_set():
        
        wuzek.set_speed(EEG_obj.get_stright_output())
        wuzek.set_steer(EEG_obj.get_turn_output())
        
        print(f"Predkosc: " + str(EEG_obj.get_stright_output()) + "\n Skret: " + str(EEG_obj.get_turn_output))  # Debugging wartości 

        # Opóźnienie dla płynniejszego działania
        time.sleep(0.05)

    print("Sterowanie eeg zakończone.")



"""
name = find_know_face()

print(name)

camera = cv2.VideoCapture(0)  # Pierwsza dostępna kamera
face_analyzer = FaceAnalyzer(True, [camera])  # Inicjalizacja FaceAnalyzer z kamerą
face_analyzer.start()

tell_hello(audio_player, name)
tell_help_you(audio_player)

recognizer_audio = RealTimeRecognizer()
recognizer_audio.start()

port = "/dev/ttyUSB0"
baud_rate = 115200

wuzek = ChairConnect(port, baud_rate)
wuzek.start()

while True:
    time.sleep(0.1)
    tranckrypcja = ""
    if True in face_analyzer.get_speaking_status():
        recognizer_audio.start_recording()
        print(face_analyzer.get_speaking_status())
        pass
    else:
        tranckrypcja = recognizer_audio.stop_recording()
        pass

    tranckrypcja = tranckrypcja.strip().lower()


    if "sterowanie aplikacją" in tranckrypcja:
        print("włączam sterowanie aplikacją")
        
    elif "kalibracja głowa" in tranckrypcja:
        recognizer_audio.stop()
        kalibracja(audio_player, face_analyzer)
        recognizer_audio.start()
        print("włączam sterowanie eeg")
    elif "test wózka" in tranckrypcja:
        start_new_thread(test_wuzka)
    elif "ustaw na 100" in tranckrypcja:
        start_new_thread(ustaw_na)

    elif "sterowanie głową" in tranckrypcja:
        start_new_thread(sterowanie_głową)

    elif "sterowanie eeg" in tranckrypcja:
        start_new_thread(sterowanie_eeg)

    elif "wyłącz się" in tranckrypcja:
        print("wyłączam się")
        tell_end(audio_player)
        recognizer_audio.stop()
        face_analyzer.stop()
        wuzek.stop()
        if active_thread and active_thread.is_alive():
            stop_thread_event.set()
            active_thread.join()
        sys.exit()
        break
    else:
        if tranckrypcja != "":
            beep(400, 0.1)
"""
class Main:

    def __init__(self):
        
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.AUDIO_PATH = os.path.join(base_dir, 'voice')
        self.FACE_PATH= os.path.join(base_dir, 'face')

        self.recognizer_audio = RealTimeRecognizer()
        self.AUDIO_CONTROL= False

        self.audio_player = AudioPlayer(AUDIO_PATH)

        self.audio_thread = None
        self.active_thread = None
        self.stop_thread_event = threading.Event()

        self.check_system()

        self.port = "COM8"
        self.baud_rate = 115200

        self.wheelchair = ChairConnect(self.port, self.baud_rate)
        self.camera = cv2.VideoCapture(0)  #First avaliable camera
        self.face_analyzer = FaceAnalyzer(True, [self.camera])   
        self.human_tracker = HumanTracker()

        self.speed = 0 
        self.turn = 0
        
        self.MAX_SPEED = 100
        self.MAX_TURN = 100
        self.MIN_SPEED = -100
        self.MIN_TURN = -100

        self.wheelchair_startup()          

    def check_system(self):
        if(sys.platform =="linux"):
            print("linux")
            self.port = "/dev/ttyUSB0"
            self.baud_rate = 115200

        elif(sys.platform == "win32"):
            print("windows")


    def wheelchair_startup(self):

        self.wheelchair.start()


    #start_new_thread called every time new steering method is selected

    def start_new_thread(self, function, *args):
        """
        Starts new thread using given function, while stopping priveus thread
        """
        self.speed = 0
        self.turn = 0
        self.wheelchair.set_speed(self.speed)
        self.wheelchair.set_steer(self.turn)

    
        if self.active_thread and self.active_thread.is_alive():
            self.stop_thread_event.set()
            self.active_thread.join()

        
        self.stop_thread_event.clear()

        
        self.active_thread = threading.Thread(target=function, args=args)
        self.active_thread.start()
   
    def stop_thread(self):
        self.speed = 0
        self.turn = 0
        self.wheelchair.set_speed(self.speed)
        self.wheelchair.set_steer(self.turn)

        if self.active_thread and self.active_thread.is_alive():
                self.stop_thread_event.set()
                self.active_thread.join()

                



    #functions to operate inside of other methods

    def Play_audio(self, audio_f_name):
        #print(name)
        self.audio_player.play_audio(audio_f_name)
        #time.sleep(2) 
                   
    def transcribe_audio(self):
        while True:
            time.sleep(0.1)
            if True in self.face_analyzer.get_speaking_status():
                self.recognizer_audio.start_recording()
                print(self.face_analyzer.get_speaking_status())
                pass
            else:
                self.input_text = self.recognizer_audio.stop_recording()
                pass

    def find_known_face(self):
        self.camera = cv2.VideoCapture(0)  # Pierwsza dostępna kamera
        face_recognition_system = Recognize_face(FACE_PATH, VIDEO_FACE_COMPARE, camera)
        name = face_recognition_system.wait_for_face()
        face_recognition_system.video_capture.release()  # Zwolnij kamerę jawnie po zakończeniu
        cv2.destroyAllWindows()  # Zamknij wszystkie okna
        del face_recognition_system

        # Upewnij się, że kamera została zwolniona
        while self.camera.isOpened():
            self.camera.release()
            time.sleep(0.1)

        return name

    def head_calibration(self):
        # Kalibracja pozycji środkowej dla wszystkich kamer
        self.audio_player.play_audio("kalibracja", "przud")
        time.sleep(1)
        self.face_analyzer.calibrate_center()
        self.audio_player.play_audio("kalibracja", "lewo")
        time.sleep(1)
        self.face_analyzer.calibrate_left()
        self.audio_player.play_audio("kalibracja", "prawo")
        time.sleep(1)
        self.face_analyzer.calibrate_right()
        self.audio_player.play_audio("kalibracja", "zakończono") 

    def change_speed(self, value):
        self.speed = self.speed + value
        if(self.speed >= self.MAX_SPEED):
            self.speed = self.MAX_SPEED
        elif (self.speed <= self.MIN_SPEED):
            self.speed = self.MIN_SPEED

    def change_turn(self, value):
        self.turn = self.turn + value
        if(self.turn >= self.MAX_TURN):
            self.turn = self.MAX_TURN
        elif (self.turn <= self.MIN_TURN):
            self.turn = self.MIN_TURN




    #Steering method functions, call them as start_new_thread argument

    def head_steering(self):
        self.face_analyzer.start()

        self.head_calibration()

        print("head steering active")

        while not self.stop_thread_event.is_set():

            normalized_gaze = self.face_analyzer.get_normalized_gaze()

            if normalized_gaze is None or normalized_gaze[0] is None:
                print("Cant read user face, make sure the camera is working properly")
                time.sleep(0.1)
                continue


            ster_value = max(min(int(normalized_gaze[0]), self.MAX_TURN), self.MIN_TURN)
            print(f"Steering: {ster_value}")  # Debugging wartości sterowania

            self.wheelchair.set_steer(ster_value)
            self.wheelchair.set_speed(self.speed) 

            time.sleep(0.05)

        print("head steering finished")
        self.face_analyzer.stop()

    def EEG_steering(self):
    
        print("EEG steering is active")

        EEG_obj = EEG_manager()

        while not self.stop_thread_event.is_set():
            
            self.wheelchair.set_speed(EEG_obj.get_stright_output())
            self.wheelchair.set_steer(EEG_obj.get_turn_output())
            
            #print(f"Predkosc: " + str(EEG_obj.get_stright_output()) + "\n Skret: " + str(EEG_obj.get_turn_output))   

            time.sleep(0.05)

        print("EEG steering finished")

    def button_steering(self):

        print("button steering is active")
       
        while not self.stop_thread_event.is_set():
                
                self.wheelchair.set_speed(self.speed)
                self.wheelchair.set_steer(self.turn)

                time.sleep(0.05)
        print("button steering finished")

    def following(self):
        print("silhouette tracking is active")

       
        self.human_tracker.start_detection()

        while not self.stop_thread_event.is_set():
            
            self.wheelchair.set_steer(self.human_tracker.get_offset())
            self.wheelchair.set_speed(self.speed)
          
            time.sleep(0.05)

        print("EEG steering finished")



                    

    def quit(self):
        self.recognizer_audio.stop()
        self.face_analyzer.stop()
        self.wheelchair.stop()
        if self.active_thread and self.active_thread.is_alive():
            self.stop_thread_event.set()
            self.active_thread.join()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()
        sys.exit()


    #test methods
    def test_wheelchair():

        beep(400, 0.1)

        pass


    def beep(frequency, duration, samplerate=22050):
        """
        generates sound of given frequency and duration
        """
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        sd.play(wave, samplerate=samplerate, blocksize=1024, latency='high')
        sd.wait()

if __name__ == "__main__":
    a = Main()