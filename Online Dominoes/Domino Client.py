import socket
##basically all vibecoded T_T
class DominoClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print("Connected to the server.")
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