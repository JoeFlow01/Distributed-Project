import socket
import threading
from SurroundingsFile import Surroundings
import pickle
from PlayerFile import Player
import time


class CarRacingServer:

    def __init__(self):
        self.global_surroundings = Surroundings()
        self.host = "localhost"  # Server IP address
        self.port = 5050  # Server port
        self.server_socket = None
        self.connections = []
        self.players = []

    def print_objects(self, list):
        for i in list:
            print(vars(i))

    def update_player(self, player):
        for i in range(len(self.players)):
            if self.players[i].username == player.username:
                self.players[i] = player
                return

    def register_player(self, player):
        if player.username.strip() == "":
            return "Enter a username"

        for i in self.players:
            if i.username == player.username:
                return "User name already exists"
        self.players.append(player)
        return "Login Successful, Joining the game"

    def update_map(self):

        while True:
            if self.global_surroundings.game_ended:
                serialized_data = pickle.dumps(self.global_surroundings)
                for client_socket in self.connections:
                    try:
                        client_socket.send(serialized_data)
                    except socket.error:
                        print("Socket is closed")
                self.global_surroundings = Surroundings()
                print("Game 5les ya ged3aan")
                print(vars(self.global_surroundings))
                self.players = []
                for current_socket in self.connections:
                    current_socket.close()
                    self.connections.remove(current_socket)
                self.connections = []
                print("players:")
                self.print_objects(self.players)
                print("Connections:")
                print(self.connections)
                self.global_surroundings.game_ended = False
                self.global_surroundings.game_started = False

                print("Reseting done, Number of connections:",len(self.connections))

            for player in self.players:
                if player.crashed:

                    self.players.remove(player)
            if len(self.players) > 0:
                self.global_surroundings.game_started = True

            #if (len(self.players) <= 1) and self.global_surroundings.game_started:
            #    print("game about to end")
             #   self.global_surroundings.game_ended = True
              #  print("game ended:",self.global_surroundings.game_ended)

            time.sleep(0.01)

    def receive_data(self, client_socket):
        while True:
            try:
                sterilized_object = client_socket.recv(2048)
                received_object = pickle.loads(sterilized_object)
                if isinstance(received_object, Player):
                    self.update_player(received_object)
                    break
            except Exception:
                client_socket.close()
                break
                print("fashel begad")

    def start(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print('Server started on {}:{}'.format(self.host, self.port))
        updating_thread = threading.Thread(target=self.update_map)
        updating_thread.start()
        while True:
            client_socket, client_address = self.server_socket.accept()
            print('New connection from {}:{}'.format(client_address[0], client_address[1]))
            connection_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            connection_thread.start()
            print("number of connections:", len(self.connections))

    def handle_client(self, client_socket):
        self.connections.append(client_socket)
        while True:
            try:
                message = client_socket.recv(1024).decode()
                username = message.split(",")[1]
                player = Player()
                player.username = username
                msg = self.register_player(player)
                client_socket.send(msg.encode())
                if msg == "Login Successful, Joining the game":
                    break
            except socket.error:
                print("Socket is closed")
                break

        while True:
            try:
                if not self.global_surroundings.game_ended:
                    # receive player
                    self.receive_data(client_socket)

                    # send surroundings

                    serialized_data = pickle.dumps(self.global_surroundings)
                    try:
                        client_socket.send(serialized_data)
                    except OSError as e:
                        print(f"Error occurred while sending data: {e}")
                        break


                    # send players
                    serialized_data = pickle.dumps(self.players)
                    try:
                        client_socket.send(serialized_data)
                    except OSError as e:
                        print(f"Error occurred while sending data: {e}")
                        break


            except socket.error:
                print("removing client due to errors in sending and receiving data")
                self.connections.remove(client_socket)
                client_socket.close()
                break


if __name__ == '__main__':
    server = CarRacingServer()
    server.start()
