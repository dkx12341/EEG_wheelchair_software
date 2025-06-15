import threading
import time
import speech_recognition as sr
import webrtcvad


#debug
import cv2
from analyze_face import FaceAnalyzer
#

VAD_LEVEL = 2#2   
THRESHOLD = 0.1 #0.2
LOOP_DELAY = 0.1#0.1

class RealTimeRecognizer:
    def __init__(self):
        """
        Initializes the real-time speech recognizer to transcribe spoken words.
        """
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad(VAD_LEVEL)
        self.recording_flag = False
        self.stop_recording_flag = False
        self.transcription = ""
        self.thread = threading.Thread(target=self._record_and_recognize)
        self.running = False
        self.clear = False

    def start(self):
        """Starts the audio recording thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._record_and_recognize)
            self.thread.start()

    def stop(self):
        """Stops the audio recording thread."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def _is_speech_present(self, audio_data, sample_rate=16000, frame_duration_ms=30):
        """
        Checks if speech is present in the given audio data based on VAD thresholds.

        Parameters:
        - audio_data: The raw audio data to analyze.
        - sample_rate: Sampling rate of the audio data (default is 16000 Hz).
        - frame_duration_ms: Duration of each frame in milliseconds (default is 30 ms).

        Returns:
        - Boolean indicating whether speech is present in the audio sample.
        """
        frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
        frames = [audio_data[i:i + frame_size] for i in range(0, len(audio_data), frame_size)]
        frames = [frame for frame in frames if len(frame) == frame_size]
        speech_frames = sum(1 for frame in frames if self._safe_is_speech(frame, sample_rate))
        return (speech_frames / len(frames)) >= THRESHOLD

    def _safe_is_speech(self, frame, sample_rate):
        """
        Safely checks if a frame contains speech using VAD, with error handling.

        Parameters:
        - frame: Audio frame data.
        - sample_rate: Sampling rate of the audio data.

        Returns:
        - Boolean indicating whether the frame contains speech.
        """
        try:
            return self.vad.is_speech(frame, sample_rate)
        except webrtcvad.Error:
            print("Error processing audio frame.")
            return False

    def _record_and_recognize(self):
        """
        The main thread function for recording and recognizing speech in real time.
        Uses a microphone to capture audio and transcribe spoken words.
        """
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Ambient noise calibration completed.")
            while self.running:
                if self.recording_flag:
                    print("Recording started...")
                    self.stop_recording_flag = False
                    try:
                        self.transcription = ""
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        audio_data = audio.get_raw_data()
                        with open("test.wav", "wb") as f:
                            f.write(audio.get_wav_data())
                            print("Audio saved for debugging.")

                        if self._is_speech_present(audio_data):#self._is_speech_present(audio_data):
                            segment_text = self.recognizer.recognize_google(audio)#self.recognizer.recognize_google(audio, language="pl-PL")
                            self.transcription = segment_text
                            print("Segment transcription:", segment_text)
                        else:
                            print("No speech detected in sample.")

                    except sr.UnknownValueError:
                        print("Could not understand the audio.")
                    except sr.WaitTimeoutError:
                        print("Timeout: No sound detected within the allowed time.")
                    except sr.RequestError:
                        print("Error connecting to the speech recognition server.")

                    self.recording_flag = False
                    print("Recording stopped.")

                if self.clear:
                    self.clear_buffer()
                    self.clear = False

                time.sleep(LOOP_DELAY)

    def start_recording(self):
        """Sets the flag to start recording audio."""
        self.recording_flag = True

    def stop_recording(self):
        """Stops the recording and returns the transcription of the last audio segment."""
        if self.recording_flag:
            self.stop_recording_flag = True
            while self.recording_flag:
                time.sleep(LOOP_DELAY)
            transcription = self.transcription
            self.transcription = ""
            return transcription
        else:
            return ""


# if __name__ == "__main__":
#     detector = RealTimeRecognizer()
#     analyzer = FaceAnalyzer(True,[cv2.VideoCapture(0)])
#     while True:
#             time.sleep(0.1)
#             if True in analyzer.get_speaking_status():
#                 detector.start_recording()
#                 print(analyzer.get_speaking_status())
#                 pass
#             else:
#                 print(detector.stop_recording())
#                 pass
    
    