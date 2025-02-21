import string
from collections import Counter
import socket



class EEG_manager:

    straight_output = 0
    straight_output_max = 100
    straight_output_min = -100
    straight_output_change = 20

    turn_output = 0 
    turn_output_max = 100
    turn_output_min = -100
    turn_output_change = 20

    buffor_length = 5
    EEG_command_buffor =[]

    server_host = "127.0.0.1"  # Change to the server's IP address if needed
    server_port = 2000       # Change to the server's port if needed

    def __init__(self):
        
        self.receive_data_from_server( self.server_host, self.server_port)
        pass

   

    def receive_data_from_server(self, server_host, server_port):
        try:
            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connect to the server
            client_socket.connect((server_host, server_port))
            print(f"Connected to server {server_host}:{server_port}")
            
            # Receive data from the server
            while True:
                data = client_socket.recv(1024).decode('utf-8')  # Receive up to 1024 bytes
                if not data:
                    print("Connection closed by the server.")
                    break
                
                
                #print(f"Received from server: {data}")

                self.EEG_command_buffor.append(data)
                
                #print(f"Received from server: {data}")
                if len(self.EEG_command_buffor) >= self.buffor_length:
                    self.adjust_output()
                    print ("straight output: " + str(self.straight_output) +"\n turn output: " + str(self.turn_output))

                
        except ConnectionRefusedError:
            print(f"Could not connect to server at {server_host}:{server_port}. Is it running?")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the socket connection
            client_socket.close()
            print("Connection closed.")
    
 
    def adjust_output(self):
        curr_command = self.find_major_command()
        self.EEG_command_buffor.clear()
        if curr_command == "neutral"  or curr_command ==  None:
            self.handle_neutral()
            return

        if curr_command == "push" or curr_command ==  "pull":
            self.handle_straight_command(curr_command)
            return
        
        if curr_command == "right" or curr_command == "left":
            self.handle_turn_command(curr_command)
            return


    def handle_neutral(self):
        if self.turn_output == 0:
            return
        if self.turn_output > 0:
            self.turn_output = self.turn_output - self.turn_output_change
            return
        if self.turn_output < 0:
            self.turn_output = self.turn_output + self.turn_output_change
            return

        if self.straight_output == 0:
            return

        if self.straight_output > 0:
            self.straight_output = self.straight_output - self.straight_output_change
            return
        if self.straight_output < 0:
            self.straight_output = self.straight_output + self.straight_output_change
            return


    def handle_straight_command(self, command):
        if self.turn_output > 0:
                self.turn_output = self.turn_output - self.turn_output_change
                return
        if self.turn_output < 0:
                self.turn_output = self.turn_output + self.turn_output_change
                return
        

        if command == "push" and self.straight_output < self.straight_output_max:
            self.straight_output = self.straight_output + self.straight_output_change
            return

        if self.straight_output > self.straight_output_min:
            self.straight_output = self.straight_output - self.straight_output_change
            return


    def handle_turn_command(self,command):
        if self.straight_output > 0:
            self.straight_output = self.straight_output - self.straight_output_change
            return
        if self.straight_output < 0:
            self.straight_output = self.straight_output + self.straight_output_change
            return

        if command == "right" and self.turn_output < self.turn_output_max:
            self.turn_output = self.turn_output + self.turn_output_change
            return

        if self.turn_output > self.turn_output_min:
            self.turn_output = self.turn_output - self.turn_output_change
            return


    def find_major_command(self):
        command_counts = Counter(self.EEG_command_buffor)
    
        max_count = max(command_counts.values())
        max_commands = [string for string, count in command_counts.items() if count == max_count]
        
        if len(max_commands) > 1:
            return "none"
        
        return max_commands[0]
        
    
    def get_stright_output(self):
        return self.straight_output
    
    def get_turn_output(self):
        return self.turn_output
    
    def get_EEG_buffor(self):
        return self.EEG_command_buffor

    



    