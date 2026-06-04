import socket
from config import *
import json
from util import *

class SocketClient():
    def __init__(self):
        self.clientSocket = None
        self.state = "disconnected"

    def connect(self):
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect((HOST, PORT))
            self.state = "connected"
            # print(f"Socket: Connected to the server. {self.clientSocket.getpeername()}")
        except Exception as e:
            print(f"Socket: Connection error: {e}")
    
    def sendMessage(self, type, content):
        packet = {
            "type": type,
            "content": content
        }
        self.sendPacket(jsonDump(packet))
    
    def receiveMessage(self):
        packet = self.receivePacket()
        return jsonLoad(packet)

    def sendPacket(self, packet):
        try:
            if self.clientSocket and self.state == "connected":
                self.clientSocket.sendall(packet.encode())
                # print(f"Socket: Sent: {packet}")
            else:
                print("Socket: Not connected to the server.")
        except Exception as e:
            print(f"Socket: Send error: {e}")

    def receivePacket(self):
        try:
            if self.clientSocket and self.state == "connected":
                # print("Socket: Waiting for message from server...")
                packet = self.clientSocket.recv(1024).decode()
                # if packet:
                    # print(f"Socket: Received: {packet}")
                return packet
            else:
                print("Socket: Not connected to the server.")
                return None
        except Exception as e:
            # print(f"Socket: Receive error: {e}")
            pass
            return None

    def close(self):
        if self.clientSocket:
            self.state = "disconnected"
            self.clientSocket.close()
            print("Socket: Connection closed.")