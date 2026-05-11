import socket
from config import *

class SocketServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(NUM_PLAYERS)
        print(f"Server started on {HOST}:{PORT}, waiting for {NUM_PLAYERS} players to connect...")
        self.accept_players()
    
    def accept_players(self):
        self.clients = []
        for i in range(NUM_PLAYERS):
            client_socket, addr = self.server_socket.accept()
            print(f"Player {i+1} connected from {addr}")
            self.clients.append(client_socket)
        
    def send(self,client, message):
        try:
            client.sendall(message.encode())
            print(f"Sent to {client.getpeername()}: {message}")
        except Exception as e:
            print(f"Error sending to {client.getpeername()}: {e}")
    
    def receive(self, client):
        try:
            message = client.recv(1024).decode()
            print(f"Received from {client.getpeername()}: {message}")
            return message
        except Exception as e:
            print(f"Error receiving from {client.getpeername()}: {e}")
            return None
    
    def close(self):
        self.server_socket.close()
        print("Server closed.")