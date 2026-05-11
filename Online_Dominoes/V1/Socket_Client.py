import socket
from config import *

class Socket_Client():
    def __init__(self):
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            print(f"Connected to the server. {self.client_socket.getpeername()}")
        except Exception as e:
            print(f"Connection error: {e}")

    def send_message(self, message):
        try:
            if self.client_socket:
                self.client_socket.sendall(message.encode())
                print(f"Sent: {message}")
            else:
                print("Not connected to the server.")
        except Exception as e:
            print(f"Send error: {e}")

    def receive_message(self):
        try:
            if self.client_socket:
                print("Waiting for message from server...")
                response = self.client_socket.recv(1024).decode()
                print(f"Received: {response}")
                return response
            else:
                print("Not connected to the server.")
                return None
        except Exception as e:
            print(f"Receive error: {e}")
            return None

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")