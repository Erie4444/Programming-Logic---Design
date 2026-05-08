from Socket_Client import Socket_Client
import threading
from config import *
import json
from Dominoes_Logic import *

class Player:
    def __init__(self, name):
        self.client = Socket_Client()
        self.running = True
        self.name = name
        self.hand = Hand([])
        self.client.connect()
        self.listen_thread = threading.Thread(target=self.listen_to_server, daemon=True)
        self.listen_thread.start()
        while self.running:
            domino_input = input(f"Current hand: {self.hand}")
            end_input = input("End to play on (left/right): ")
            self.playDomino(self.hand.getList()[int(domino_input)], end_input)

    def listen_to_server(self):
        while self.running:
            message = self.client.receive_message()
            if message:
                self.handle_server_message(message)

    def handle_server_message(self, message):
        try:
            data = json.loads(message)
            print(data)
            if data["type"] == "hand":
                self.receive_hand(data["hand"])
            
            if data["type"] == "server_shutdown":
                print(data["message"])
                self.running = False
                self.client.close()
            
            if data["type"] == "invalid_move":
                print(data["message"])
            # Handle other message types (e.g., game state updates) here
        except json.JSONDecodeError:
            print(f"Received non-JSON message: {message}")

    def receive_hand(self, hand_data):
        self.hand = Hand([Domino(tuple(d)) for d in hand_data])
        print(f"{self.name} received hand: {self.hand}")
        
    
    def playDomino(self, domino, end):
        if domino in self.hand.dominoes:
            self.hand.removeDomino(domino)
            packet = {
                "type": "play",
                "domino": domino.tuple(),
                "end": end
            }
            self.client.send_message(json.dumps(packet))
        else:
            print("Domino not in hand")
        

test_player = Player("Bob")