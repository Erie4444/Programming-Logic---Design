import socket
from config import *
import json
from util import *

class SocketServer:
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = "running"
        self.serverSocket.bind((HOST, PORT))
        self.serverSocket.listen(CAPACITY)
        print(f"Socket: Server started on {HOST}:{PORT}, waiting for {NUM_PLAYERS} players to connect...")
    
    def acceptClients(self):
        self.clients = {"PLAYERS":[], "SPECTATORS":[]}
        for i in range(CAPACITY):
            clientSocket, addr = self.serverSocket.accept()
            if len(self.clients["PLAYERS"]) < NUM_PLAYERS: ##if theres still room for players
                self.clients["PLAYERS"].append(clientSocket)
                self.sendMessage(clientSocket, "connectedPlayer", {"message": f"Welcome Player {len(self.clients['PLAYERS'])}!"})
                print(f"Socket: Player {i+1} connected from {addr}")
            else:
                self.clients["SPECTATORS"].append(clientSocket)
                self.sendMessage(clientSocket, "connectedSpectator", {"message": "You are now a spectator."})
                print(f"Socket: Spectator connected from {addr}")

    def sendPacket(self,client, packet):
        try:
            client.sendall(packet.encode())
            print(f"Socket: Sent to {client.getpeername()}: {packet}")
        except Exception as e:
            print(f"Socket: Error sending to {client.getpeername()}: {e}")
    
    def receivePacket(self, client):
        try:
            packet = client.recv(1024).decode()
            return packet
        except Exception as e:
            print(f"Socket: Error receiving from {client.getpeername()}: {e}")
            return None
    
    def receiveMessage(self, client):
        packet = self.receivePacket(client)
        return jsonLoad(packet)
    
    def broadcastPacket(self, packet, clientType=None, amount = None):
        if clientType:
            clients = self.clients[clientType]
        else:
            clients = self.getPlayers() + self.getSpectators()
        
        if amount == None:
            amount = len(clients)

        for client in clients:
            if amount <= 0:
                break
            self.sendPacket(client, packet)
            amount-=1

    def broadcastMessage(self, type, content, clientType=None, amount = None):
        packet = {
            "type": type,
            "content": content
        }
        self.broadcastPacket(jsonDump(packet), clientType,amount)
    
    def sendMessage(self, client, type, content):
        packet = {
            "type": type,
            "content": content
        }
        self.sendPacket(client, jsonDump(packet))
    
    def sendMessageToPlayer(self, playerIndex, type, content):
        if 0 <= playerIndex < len(self.clients["PLAYERS"]):
            self.sendMessage(self.clients["PLAYERS"][playerIndex], type, content)
        else:
            print(f"Socket: Invalid player index: {playerIndex}")
    
    def status(self):
        print(f"Socket: Server status: {self.state}")
        print(f"Socket: Connected clients: {[client.getpeername() for client in self.getPlayers() + self.getSpectators()]}")
        print(f"Socket: Players: {len(self.clients['PLAYERS'])}/{NUM_PLAYERS}, Spectators: {len(self.clients['SPECTATORS'])}")
    
    def getClients(self):
        return self.clients

    def getClientsList(self):
        return self.clients["PLAYERS"] + self.clients["SPECTATORS"]

    def getPlayers(self):
        return self.clients["PLAYERS"]

    def getSpectators(self):
        return self.clients["SPECTATORS"]
    
    def close(self):
        self.serverSocket.close()
        self.state = "stopped"
        print("Socket: Server closed.")