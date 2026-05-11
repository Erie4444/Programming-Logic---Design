from Socket_Server import SocketServer
from config import *
from Dominoes_Logic import *
import json
import threading

class ServerMain():
    def __init__(self):
        self.running = True
        self.current_player_index = 0
        self.server = SocketServer()
        self.boneyard = Boneyard()
        self.boneyard.shuffle()
        self.board = Board()
        self.listen_thread = threading.Thread(target=self.listen_to_clients, daemon=True)
        self.listen_thread.start()
        self.dealHands()
        print(self.server.clients)
        input("Press Enter to stop the server...")


    def dealHands(self):
        # Deal hands to players
        print("Dealing hands to players...")
        hands = [[self.boneyard.drawDomino().tuple() for _ in range(PLAYER_HAND_LIMIT)] for _ in range(NUM_PLAYERS)]
        for player in range(NUM_PLAYERS):
            packet = {
                "type": "hand",
                "hand": hands[player]
            }
            self.server.send(self.server.clients[player], json.dumps(packet))
        print("Hands dealt to players.")
    
    def listen_to_clients(self):
        while self.running:
            for client in self.server.clients:
                message = json.loads(self.server.receive(client))
                if message:
                    print(f"Received from {client.getpeername()}: {message}")
                    if client == self.server.clients[self.current_player_index]:
                        if message["type"] == "play":
                            self.playDomino(message["domino"], message["end"])
                    # Here you would handle the message and update game state accordingly
    
    def stopServer(self):
        packet = {
            "type": "server_shutdown",
            "message": "Server is shutting down."
        }
        for client in self.server.clients:
            self.server.send(client, json.dumps(packet))
        self.running = False
        self.server.close()
    
    def playDomino(self, domino, end):
        if self.board.placeDomino(Domino(tuple(domino)), end):
            print(f"Player {self.current_player_index + 1} played {domino} on the {end} end.")
            self.current_player_index = (self.current_player_index + 1) % NUM_PLAYERS
            print(self.board)
        else:
            print(f"Invalid move by player {self.current_player_index + 1}: cannot place {domino} on the {end} end.")
            packet = {
                "type": "invalid_move",
                "message": f"Cannot place {domino} on the {end} end."
            }
            self.server.send(self.server.clients[self.current_player_index], json.dumps(packet))
    
    # # Main game loop (simplified)
    # while True:
    #     for i, client in enumerate(self.server.clients):
    #         # Send player's hand
    #         hand_str = "Your hand: " + str(hands[i])
    #         server.send(client, hand_str)
            
    #         # Receive player's move (simplified)
    #         move = client.recv(1024).decode()
    #         print(f"Player {i+1} move: {move}")
            
    #         # Process move and update game state (not implemented)
    #         # ...
            
    #         # Check for game end condition (not implemented)
    #         # ...

test_server = ServerMain()