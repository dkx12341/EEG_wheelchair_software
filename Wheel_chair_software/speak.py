import os
import pygame
import time
from pydub import AudioSegment
import simpleaudio as sa

class AudioPlayer:
    def __init__(self, base_path):
        """
        Initializes the audio player with a base path to the audio folders.

        Parameters:
        - base_path: The root directory containing folders with audio files.
        """
        self.base_path = base_path
        pygame.mixer.init()
        self.current_wave_obj = None

    def play_audio(self, folder, filename):
        """
        Searches for an audio file in the specified folder with the given filename (without extension)
        and plays it if found. Supports multiple audio formats.

        Parameters:
        - folder: Name of the subdirectory within the base path where the audio file is located.
        - filename: The name of the audio file without the extension.
        """
        folder_path = os.path.join(self.base_path, folder)

        audio_extensions = ['.mp3', '.wav', '.ogg', '.flac']

        for ext in audio_extensions:
            file_path = os.path.join(folder_path, filename + ext)
            if os.path.isfile(file_path):
                print(f"Playing file: {file_path}")

                if ext == '.flac':
                    audio = AudioSegment.from_file(file_path, format="flac")
                    self.current_wave_obj = sa.WaveObject(
                        audio.raw_data,
                        audio.channels,
                        audio.sample_width,
                        audio.frame_rate
                    )
                    play_obj = self.current_wave_obj.play()
                    play_obj.wait_done()
                else:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                return

        print("Audio file not found.")

    def stop_audio(self):
        """
        Stops audio playback for both pygame and simpleaudio (used for .flac files).
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
