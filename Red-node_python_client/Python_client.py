import socket
from EEG_manager import EEG_manager

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
            
            print(f"Received from server: {data}")
            self.EEG_command_buffor.append(data)

            
    except ConnectionRefusedError:
        print(f"Could not connect to server at {server_host}:{server_port}. Is it running?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the socket connection
        client_socket.close()
        print("Connection closed.")



EEG_manager.receive_data_from_server = receive_data_from_server
"""
if __name__ == "__main__":
    # Server configuration
    SERVER_HOST = "127.0.0.1"  # Change to the server's IP address if needed
    SERVER_PORT = 2000       # Change to the server's port if needed
    
    receive_data_from_server(SERVER_HOST, SERVER_PORT)"""