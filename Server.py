import socket
import threading
from SurroundingsFile import Surroundings
import pickle
from PlayerFile import Player
from pymongo import MongoClient
import pymongo.errors
import sys

import time
import random


# connection_string = "mongodb+srv://ammarsaad11223:58p3dmtE6Js7YMIS@cluster0.qsveoyz.mongodb.net/?retryWrites=true&w=majority"

connection_string = "mongodb+srv://OsamaAmr:nxCyIg0JjK6nMT1x@cluster0.xswtiie.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)
databaseMain = client["CarGameDB"]
collection = databaseMain["CarGame"]
databaseReplica = client["CarGame2"]
collection1 = databaseReplica["CarGame2"]
databases = [collection, collection1]

# Check database connection
def checkDatabaseConnection():
    global database
    global databases
    try:
        if databaseMain.command('ping')['ok'] == 1:
            print("Successfully connected to MongoDB Main database!")
            database = databaseMain
            databases = [databaseMain]
        elif databaseReplica.command('ping')['ok'] == 1:
            print("Successfully connected to MongoDB Replica database!")
            database = databaseReplica
            databases = [databaseReplica]
        else:
            print("Failed to connect to MongoDB both Main and Replica databases!")
        if databaseMain.command('ping')['ok'] == 1 and databaseReplica.command('ping')['ok'] == 1:
            databases = [databaseMain, databaseReplica]
    except pymongo.errors.ConnectionFailure as e:
        print("Failed to connect to MongoDB databases:", e)
        sys.exit()


def write_to_database(data):
    try:
        collection.insert_one(data)
        collection1.insert_one(data)
        print("Data successfully written to the database.")
    except Exception as e:
        print("Failed to write data to the database:", e)

def read_from_database():
    try:
        data = list(collection.find())
        if data:
            return data
        else:
            print("No data found in the database.")
    except Exception as e:
        print("Failed to read data from the database:", e)

def read_from_database2():
    try:
        data = collection1.find_one()
        if data:
            return data
        else:
            print("No data found in the database.")
    except Exception as e:
        print("Failed to read data from the database:", e)


data_from_db = read_from_database2()
print("Data from the database:", data_from_db)

# Example usage:
# data_to_write = {"username": "John", "score": 100}
# write_to_database(data_to_write)
#
# data_from_db = read_from_database()
# print("Data from the database:", data_from_db)









class CarRacingServer:

    def __init__(self):
        self.current_player = None
        self.global_surroundings = Surroundings()
        self.host = "localhost"  # Server IP address
        self.port = 5050  # Server port
        self.server_socket = None
        self.players = []
        self.lock = threading.Lock()

    def sort_players_by_distance(self, players):
        sorted_players = sorted(players, key=lambda laeeb: laeeb.dist_covered, reverse=True)
        for i, player in enumerate(sorted_players):
            player.position = i + 1
        return sorted_players


    def update_player(self, player):
        for i in range(len(self.players)):
            if self.players[i].username == player.username:
                self.lock.acquire()
                self.players[i] = player
                self.lock.release()
                return

    def register_player(self, player):
        if player.username.strip() == "":
            return "Enter a username"

        # Read all data entries from the database
        data_entries = read_from_database()

        # Check if the username is already taken
        for data in data_entries:
            if data.get("username") == player.username:
                return "Username already exists"

        # Create a data dictionary with the player information
        data = {"username": player.username, "position": player.position, "car_x":player.car_x_coordinate, "car_y":player.car_y_coordinate, "distance":player.dist_covered }  # Add more player attributes as needed

        # Write the data to the database
        write_to_database(data)

        self.lock.acquire()
        self.players.append(player)
        self.lock.release()
        return "Login Successful, Joining the game"

    # def update_attributes(self, players):
    #     for player in players:
    #         if player.username in self.players:
    #             if player.username == self.current_player.username:
    #                 # Update the existing attributes for the current player
    #                 self.current_player.username = player.username
    #                 self.current_player.crashed = player.crashed
    #                 self.current_player.car_x_coordinate = player.car_x_coordinate
    #                 self.current_player.car_y_coordinate = player.car_y_coordinate
    #                 self.current_player.position = player.position
    #                 self.current_player.dist_covered = player.dist_covered
    #
    #                 # Write the updated data to the database
    #
    #         else:
    #             self.players.append(player.username)
    #             if not self.current_player:
    #                 self.current_player = player
    #             # Create a data dictionary with the player's initial attributes
    #             # Write the initial data to the database
    #             data = {
    #                 "username": player.username,
    #                 "crashed": player.crashed,
    #                 "car_x_coordinate": player.car_x_coordinate,
    #                 "car_y_coordinate": player.car_y_coordinate,
    #                 "position": player.position,
    #                 "dist_covered": player.dist_covered,
    #                 "finished": player.finished,
    #                 "disconnected": player.disconnected
    #             }
    #             # ...
    #
    #     return "Player attributes updated successfully"




    # def register_player(self, player):
    #     if player.username.strip() == "":
    #         return "Enter a username"
    #
    #     for i in self.players:
    #         if i.username == player.username:
    #             return "User name already exists"
    #     self.lock.acquire()
    #     self.players.append(player)
    #     self.lock.release()
    #     return "Login Successful, Joining the game"

    def update_map(self):
        while True:
            if self.global_surroundings.game_ended:
                self.global_surroundings = Surroundings()
                print("Game 5les ya ged3aan")
                print(vars(self.global_surroundings))
                self.players = []
            if len(self.players) == 1:
                self.global_surroundings.game_started = True
            self.lock.acquire()
            self.sort_players_by_distance(self.players)
            self.lock.release()
            finished = True
            if len(self.players) < 1:
                finished = False
            for player in self.players:
                if not player.finished:
                    finished = False
                    break
            # self.update_attributes(self.players)
            self.global_surroundings.game_ended = finished

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

    def handle_client(self, client_socket):
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
                try:
                    client_socket.close()
                except:
                    print("yady elnila")
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
                        self.lock.acquire()
                        client_socket.send(serialized_data)
                        self.lock.release()
                    except OSError as e:
                        print(f"Error occurred while sending data: {e}")
                        break
            except socket.error:
                print("removing client due to errors in sending and receiving data")
                client_socket.close()
                break


if __name__ == '__main__':
    server = CarRacingServer()
    server.start()
