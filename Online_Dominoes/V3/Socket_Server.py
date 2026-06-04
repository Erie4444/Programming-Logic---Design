import socket
from config import *
import json
from util import *
import struct

class SocketServer:
    '''
    Socket Server class
    Provides functionality to connect, send, and recieve messages from clients
    '''
    def __init__(self):
        ##initializing the socket connection
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = "running"
        self.serverSocket.bind((HOST, PORT))
        self.serverSocket.listen(CAPACITY)
        # print(f"Socket: Server started on {HOST}:{PORT}, waiting for {NUM_PLAYERS} players to connect...")
    
    def acceptClients(self):
        '''
        Handles new connecting clients and assigns them to player
        or spectator based on NUM_PLAYERS
        '''
        try:
            self.clients = {"PLAYERS":[], "SPECTATORS":[]}
            while self.state == "running": ##continuously check for new clients while socket is running
                clientSocket, addr = self.serverSocket.accept()
                if len(self.clients["PLAYERS"])+len(self.clients["SPECTATORS"]) >= CAPACITY: ##checks if at max capacity
                    self.sendMessage(clientSocket,"denyConnection","")

                elif len(self.clients["PLAYERS"]) < NUM_PLAYERS: ##if theres still room for players
                    self.clients["PLAYERS"].append(clientSocket)
                    self.sendMessage(clientSocket, "connectedPlayer", {"message": f"Welcome Player {len(self.clients['PLAYERS'])}!"})
                    # print(f"Socket: Player connected from {addr}")

                else: ##adds to spectator
                    self.clients["SPECTATORS"].append(clientSocket)
                    self.sendMessage(clientSocket, "connectedSpectator", {"message": "You are now a spectator."})
                    # print(f"Socket: Spectator connected from {addr}")
        
        except Exception as e:
            pass

    '''
    OLD DEPRICATED SEND PACKET CODE
    Doesn't work as it doesn't ensure the whole packet sends
    '''
    # def sendPacket(self,client, packet):
    #     try:
    #         client.sendall(packet.encode())
    #         # print(f"Socket: Sent to {client.getpeername()}: {packet}")
    #     except Exception as e:
    #         print(f"Socket: Error sending to {client.getpeername()}: {e}")


    def sendPacket(self, client, packet):
        '''
        Sends a packet to a client
        Ensures the whole packet is sent
        '''
        try:
            data = packet.encode()
            length = struct.pack("!I", len(data))  ## 4-byte header for length of message
            client.sendall(length + data)

        except Exception as e:
            print(f"Socket: Error sending to {client.getpeername()}: {e}")

    def recv_exact(self, client, n):
        '''
        Ensures the recieved packet is the specified length (n)
        '''
        data = b""
        while len(data) < n: ##recieves until length of data is equal to the length specified
            chunk = client.recv(n - len(data)) ##recvs with buffersize equal to the length left
            if not chunk:
                return None
            data += chunk ##adds the chunk recieved to the data
        return data
    
    def receiveMessage(self, client):
        '''
        Receives a packet, using the length of the packet to ensure full packet is 
        recieved
        '''
        try:
            header = self.recv_exact(client, 4) ##getting the length of the packet
            if not header:
                return None
            length = struct.unpack("!I", header)[0] ##unpacks the header bytes
            payload = self.recv_exact(client, length) ##uses the length and runs recv_exact for the packet
            if not payload:
                return None
            return jsonLoad(payload.decode()) ##decodes the packet if it exists
        
        except Exception as e:
            print(f"Socket: Error receiving from {client.getpeername()}: {e}")
            return None
    
    def broadcastPacket(self, packet, clientType=None, amount = None):
        '''
        Broadcasts a packet to a group of clients
        ClientType specifies the type of client (PLAYERS/SPECTATORS) to broadcast to 
            (broadcasts to all if nothing is specified)
        Amount specifies the amount of clients to send to
        '''

        ##Getting a list of clients to send to
        if clientType:
            clients = self.clients[clientType]
        else:
            clients = self.getPlayers() + self.getSpectators()
        
        ##Getting the amount of clients to send to
        if amount == None:
            amount = len(clients)

        ##Sending to the clients
        for client in clients:
            if amount <= 0:
                break
            self.sendPacket(client, packet)
            amount-=1

    def broadcastMessage(self, type, content, clientType=None, amount = None):
        '''
        Broadcasts a message, using broadcastPacket to clients
        '''
        ##making the json
        packet = {
            "type": type,
            "content": content
        }
        self.broadcastPacket(jsonDump(packet), clientType,amount) ##broadcasts the packet
    
    def sendMessage(self, client, type, content):
        '''
        Sends a message to a specific client
        '''
        ##making the json
        packet = {
            "type": type,
            "content": content
        }
        self.sendPacket(client, jsonDump(packet)) ##sends the packet
    
    def sendMessageToPlayer(self, playerIndex, type, content):
        '''
        Sends a message to a specific player number
        '''
        if 0 <= playerIndex < len(self.clients["PLAYERS"]): ##if the player number is valid
            self.sendMessage(self.clients["PLAYERS"][playerIndex], type, content) ##sends the message to that player
        else:
            print(f"Socket: Invalid player index: {playerIndex}")
    
    def status(self):
        '''
        Status function, not used
        '''
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

    def clearServer(self):
        '''
        Clears the server of clients
        '''
        ##tells all clients to close
        for client in self.clients["PLAYERS"] + self.clients["SPECTATORS"]:
            self.sendMessage(client,"close","")
        ##resetting client lists
        self.clients["PLAYERS"] = []
        self.clients["SPECTATORS"] = []
    
    def close(self):
        '''
        Closes the server
        '''
        self.state = "stopped"
        self.serverSocket.close()
        print("Socket: Server closed.")