import socket
from config import *
import json
from util import *
import struct

class SocketClient():
    '''
    Socket Client class
    Provides functionality to connect, send,and receive messages from the server
    '''
    def __init__(self):
        self.clientSocket = None
        self.state = "disconnected"

    def connect(self):
        '''
        Connects to the server
        '''
        try:
            ##makes the socket and establishes the connection
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect((HOST, PORT))
            self.state = "connected"
            # print(f"Socket: Connected to the server. {self.clientSocket.getpeername()}")
        except Exception as e:
            print(f"Socket: Connection error: {e}")
    
    def sendMessage(self, type, content):
        '''
        Sends a message to the server
        '''
        ##making the json
        packet = {
            "type": type,
            "content": content
        }
        ##sending the packet
        self.sendPacket(jsonDump(packet))
    
    def receiveMessage(self):
        '''
        Handles received messages from the server
        '''
        packet = self.receivePacket() ## gets the packet from the server
        return jsonLoad(packet) ##returns the loaded message


    '''
    OLD DEPRICATED SEND PACKET CODE
    Doesn't work as it doesn't ensure the whole packet sends
    '''
    # def sendPacket(self, packet):
    #     try:
    #         if self.clientSocket and self.state == "connected":
    #             self.clientSocket.sendall(packet.encode())
    #             # print(f"Socket: Sent: {packet}")
    #         else:
    #             print("Socket: Not connected to the server.")
    #     except Exception as e:
    #         print(f"Socket: Send error: {e}")

    def sendPacket(self, packet):
        '''
        Sends a packet to the server
        Ensures the whole packet is sent by sending the length of the packet
        '''
        try:
            if self.clientSocket and self.state == "connected":
                data = packet.encode()
                length = struct.pack("!I", len(data)) ##getting the length of the packet
                self.clientSocket.sendall(length + data)
            else:
                print("Socket: Not connected to the server.")

        except Exception as e:
            print(f"Socket: Send error: {e}")

    def recv_exact(self, n):
        '''
        Ensures the data recieved is the specified number of bytes
        '''
        data = b""
        while len(data) < n: ##recv until the data is the length specified (n)
            chunk = self.clientSocket.recv(n - len(data)) ##recvs bytes with buffer equal to the bytes left
            if not chunk:
                return None
            data += chunk
        return data


    '''
    OLD DEPRICATED RECEIVE CODE
    Doesn't work as it doesn't ensure the whole packet is recieved
    '''
    # def receivePacket(self):
    #     try:
    #         if self.clientSocket and self.state == "connected":
    #             # print("Socket: Waiting for message from server...")
    #             packet = self.clientSocket.recv(1024).decode()
    #             # if packet:
    #                 # print(f"Socket: Received: {packet}")
    #             return packet
    #         else:
    #             print("Socket: Not connected to the server.")
    #             return None
    #     except Exception as e:
    #         # print(f"Socket: Receive error: {e}")
    #         pass
    #         return None

    def receivePacket(self):
        '''
        New receive code using the length of the packet to ensure the whole packet is received
        '''
        try:
            if self.clientSocket and self.state == "connected":
                header = self.recv_exact(4) ##getting the length of the packet
                if not header:
                    return None
                length = struct.unpack("!I", header)[0] ##unpacking the bytes
                payload = self.recv_exact(length) ##using recv exact() to recieve the whole packet
                if not payload:
                    return None
                return payload.decode() ##decodes the packet
            else:
                print("Socket: Not connected to the server.")
                return None

        except Exception as e:
            pass
            # print(f"Socket: Receive error: {e}")
            # return None

    def close(self):
        '''
        Closes the socket
        '''
        if self.clientSocket:
            self.state = "disconnected"
            self.clientSocket.close()
            print("Socket: Connection closed.")