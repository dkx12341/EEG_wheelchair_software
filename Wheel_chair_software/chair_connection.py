import serial
import time
import threading
import struct

# Constants for chair modes
DEFAULT_MOD = 0
PREFER_BT_MOD = 1
PREFER_UART_MOD = 2
# PREFER_JOYSTICK_MOD = 3
AUTOMATIC_MOD = 4

LONG_BYTE_ANSWER = 15
START_BYTE = b'\xAB'  # Ramka początkowa


class COMConnection:
    """
    Klasa odpowiedzialna za nawiązywanie połączenia Bluetooth lub szeregowego w systemie.
    """

    def __init__(self, port, baud_rate=115200):
        """
        Inicjalizuje klasę COMConnection.

        :param port: Port COM do połączenia (np. 'COM5').
        :param baud_rate: Prędkość transmisji szeregowej (domyślnie 115200).
        """
        self.port = port
        self.baud_rate = baud_rate
        self.connection = None

    def connect(self):
        """
        Nawiązuje połączenie z urządzeniem przez port COM.

        :return: True jeśli połączenie zakończyło się sukcesem, False w przypadku błędu.
        """
        try:
            self.connection = serial.Serial(self.port, self.baud_rate)
            print(f"Połączono z {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Nie udało się połączyć: {e}")
            self.connection = None
            return False

    def send_command(self, command):
        """
        Wysyła komendę przez połączenie COM.

        :param command: Komenda do wysłania w postaci stringa.
        :return: True jeśli komenda została wysłana, False w przypadku błędu.
        """
        try:
            if self.connection and self.connection.is_open:
                self.connection.write(command.encode())
                print(f"Wysłano komendę: {command}")
                return True
            else:
                print("Połączenie nie jest otwarte.")
                return False
        except Exception as e:
            print(f"Nie udało się wysłać komendy: {e}")
            return False

    def send_command_and_wait_for_response(self, command, timeout=0.1):
        """
        Wysyła komendę i czeka na odpowiedź, szukając ramki początkowej 'AB' (0xAB).
        Jeśli ramka początkowa nie zostanie znaleziona w odebranych danych, funkcja
        czyści bufor i przygotowuje go na kolejną porcję danych.

        :param command: Komenda do wysłania.
        :param timeout: Czas oczekiwania na odpowiedź w sekundach.
        :return: Odpowiedź od serwera w postaci bajtów lub None w przypadku braku odpowiedzi.
        """
        try:
            if self.connection and self.connection.is_open:
                # Wysłanie komendy
                self.connection.write(command.encode())
                #print(f"Wysłano komendę: {command}")

                # Ustawienie czasu zakończenia
                end_time = time.time() + timeout

                buffer = bytearray()
                message = None

                while time.time() < end_time:
                    # Odczyt dostępnych danych
                    data = self.connection.read(self.connection.in_waiting or 1)
                    if data:
                        buffer.extend(data)
                        # Szukanie ramki początkowej w buforze
                        start_indices = [i for i, byte in enumerate(buffer) if byte == START_BYTE[0]]

                        for index in start_indices:
                            # Sprawdzamy, czy od pozycji index mamy wystarczająco danych
                            if len(buffer) - index >= LONG_BYTE_ANSWER:
                                # Wycinamy wiadomość zaczynającą się od ramki początkowej
                                message = buffer[index:index + LONG_BYTE_ANSWER]
                                #print(f"Otrzymano wiadomość: {message}")
                                # Usuwamy przetworzone dane z bufora
                                buffer = buffer[index + LONG_BYTE_ANSWER:]
                                return message
                        # Jeśli bufor staje się zbyt duży, usuwamy dane przed ostatnim potencjalnym początkiem ramki
                        if len(buffer) > 2 * LONG_BYTE_ANSWER:
                            buffer = buffer[-LONG_BYTE_ANSWER:]
                    else:
                        time.sleep(0.01)  # Krótka przerwa, aby nie obciążać CPU
                # Jeśli nie znaleziono ramki początkowej w czasie timeoutu
                print("Nie znaleziono ramki początkowej w odebranych danych.")
                # Czyścimy bufor, aby przygotować go na kolejną porcję danych
                self.connection.reset_input_buffer()
                return None
            else:
                print("Połączenie nie jest otwarte.")
                return False
        except Exception as e:
            print(f"Nie udało się wysłać komendy: {e}")
            return False

    def close(self):
        """
        Zamyka połączenie COM.

        :return: True jeśli połączenie zostało zamknięte, False w przypadku błędu.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Połączenie zamknięte.")
            return True
        else:
            print("Połączenie nie jest otwarte lub już zostało zamknięte.")
            return False


class ChairConnect:
    """
    Klasa odpowiedzialna za sterowanie urządzeniem (np. wózkiem) przez połączenie Bluetooth/COM.
    """

    def __init__(self, port, baud_rate=115200, period=0.01):
        """
        Inicjalizuje klasę ChairConnect.

        :param port: Port COM do połączenia.
        :param baud_rate: Prędkość transmisji szeregowej (domyślnie 115200).
        :param period: Okres pomiędzy kolejnymi wywołaniami zadań (domyślnie 0.01s).
        """
        self.comunikator = COMConnection(port, baud_rate)
        self.speed = 0
        self.steer = 0
        self.mod = 0
        self.period = period  # W sekundach
        self.running = False
        self.thread = None
        self.wait_on_answer = True
        self.answer = None
        self.error = False

        # Zmienne odpowiedzi
        self.start_byte = 0
        self.actual_steer = 0
        self.actual_speed = 0
        self.sonar_left = 0
        self.sonar_directory = 0
        self.sonar_right = 0
        self.temp_left = 0
        self.temp_right = 0
        self.voltage_big = 0
        self.voltage_small = 0
        self.actual_mod = 0
        self.lost_data = 0
        self.end = 0

    def start(self):
        """
        Uruchamia wątek komunikacji z urządzeniem. Nawiązuje połączenie i cyklicznie wykonuje zadania.
        """
        if not self.running:
            not_err = self.comunikator.connect()
            if not_err:
                self.running = True
                self.thread = threading.Thread(target=self._run)
                self.thread.start()
                print("Wątek został uruchomiony.")
            else:
                print("Wątek nie został uruchomiony, błąd połączenia")

    def _run(self):
        """
        Prywatna metoda wykonywana w osobnym wątku. Cyklicznie wykonuje zadania.
        """
        while self.running:
            if self.wait_on_answer:
                self.run_task_wait_on_answer()
            else:
                self.run_task()
                time.sleep(self.period)  # Okres między zadaniami

            self.check_mod()

    def run_task_wait_on_answer(self):
        """
        Wysyła komendę i czeka na odpowiedź od urządzenia, a następnie przypisuje otrzymane dane
        do odpowiednich zmiennych.
        """
        message = f"{self.steer} {self.speed} {self.mod}\n"
        answer = self.comunikator.send_command_and_wait_for_response(message)

        if answer and len(answer) == LONG_BYTE_ANSWER:
            try:
                # Rozpakowanie odpowiedzi
                data = struct.unpack('<BhhBBBBBBBBBB', answer)
                # Przypisanie zmiennych
                self.start_byte = data[0]
                self.actual_steer = data[1]         # 16-bit
                self.actual_speed = data[2]         # 16-bit
                self.sonar_left = data[3]           # 8-bit
                self.sonar_directory = data[4]      # 8-bit
                self.sonar_right = data[5]          # 8-bit
                self.temp_left = data[6]            # 8-bit
                self.temp_right = data[7]           # 8-bit
                self.voltage_big = data[8]          # 8-bit
                self.voltage_small = data[9]        # 8-bit
                self.actual_mod = data[10]           # 8-bit
                self.lost_data = data[11]           # 8-bit
                self.end = data[12]                 # 8-bit

                #print(f"Odpowiedź przetworzona: {data}")
            except struct.error as e:
                print(f"Błąd przy rozpakowywaniu odpowiedzi: {e}")
        else:
            print("Nieprawidłowa odpowiedź lub brak odpowiedzi.")

    def run_task(self):
        """
        Wysyła komendę do urządzenia bez oczekiwania na odpowiedź.
        """
        message = f"{self.steer} {self.speed} {self.mod}\n"
        self.comunikator.send_command(message)

    def stop(self):
        """
        Zatrzymuje wątek komunikacji z urządzeniem i zamyka połączenie.
        """
        if self.running:
            self.set_speed(0)
            self.set_turn(0)
            time.sleep(0.3)
            self.running = False
            self.thread.join()  # Czekamy aż wątek zakończy działanie
            self.comunikator.close()
            print("Wątek został zatrzymany.")

    def check_mod(self):
        """
        Jeśli odbiornik zareaguje na zmianę mod, to wraca do neutralnego stanu.
        """
        if self.mod != 0 and self.actual_mod == self.mod:
            self.mod = 0

    def set_wait_answer(self, wait_bool):
        """
        Ustawia tryb oczekiwania na odpowiedź od urządzenia. (raczej nie używać, bo czekanie na odpowiedź synchronizuje)

        :param wait_bool: True, jeśli należy czekać na odpowiedź, False jeśli nie.
        """
        self.wait_on_answer = wait_bool

    def set_speed(self, speed):
        """
        Ustawia prędkość, która zostanie wysłana do urządzenia.

        :param speed: Prędkość w zakresie od -1000 do 1000.
        """
        if -1000 <= speed <= 1000:
            self.speed = speed

    def set_turn(self, steer):
        """
        Ustawia kierunek (skręt), który zostanie wysłany do urządzenia.

        :param steer: Wartość sterowania w zakresie od -1000 do 1000.
        """
        if -1000 <= steer <= 1000:
            self.steer = steer

    def set_mod(self, mod):
        """
        Ustawia mod, który zostanie wysłany do urządzenia.

        :param mod: Wartość mod w zakresie od 0 do 255.
        """
        if 0 <= mod <= 255:
            self.mod = mod

    def return_speed(self):
        """
        Zwraca aktualnie ustawioną prędkość.

        :return: Aktualna prędkość.
        """
        return self.speed

    def return_steer(self):
        """
        Zwraca aktualnie ustawiony kierunek (skręt).

        :return: Aktualny kierunek (skręt).
        """
        return self.steer

    def return_mod(self):
        """
        Zwraca aktualnie ustawiony mod.

        :return: Aktualny mod.
        """
        return self.mod


def main():
    # MacOS: ls /dev/tty.* dla USB np. "/dev/tty.usbserial-0001" dla BT "/dev/tty.ESP32_Robot"
    # Windows: Menadżer urządzeń => porty (COM i LPT) dla USB np. "COM6" dla BT "COM5"
    # Linux: ls /dev/tty* dla USB np. "/dev/ttyUSB0"

    #port = "/dev/ttyUSB0" #change for windows
    port = "COM3"

    baud_rate = 115200

    # Tworzymy obiekt klasy ChairConnect
    bt_connection = ChairConnect(port, baud_rate)

    # bt_connection.set_mod(PREFER_UART_MOD)

    # Uruchomienie wątku
    bt_connection.start()

    time.sleep(2)  # Czekamy 2 sekundy przed wysłaniem nowych komend

    while True:
        bt_connection.set_speed(100)
        time.sleep(2)


if __name__ == "__main__":
    main()
