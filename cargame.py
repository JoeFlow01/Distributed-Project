from time import sleep
import tkinter as tk
import pygame
from SurroundingsFile import Surroundings
from PlayerFile import Player
import socket
import pickle
import random
from Chat_Client import Client

class Enemy:
    def __init__(self,x,dist):
        self.x = x
        self.at_dist = dist


class CarRacing:

    def Generate_enemy_list(self):
        self.enemys = []
        for i in range(5000,self.race_distance*100+1000,1000):
            random.seed(i)
            x = random.randint(310, 450)
            self.enemys.append(Enemy(x, i))

    def __init__(self):
        self.race_distance = 500
        self.Generate_enemy_list()
        self.current_enemy = 0
        self.Chat_IP = 'localhost'
        self.Chat_PORT = 9090
        self.max_bg_speed = 20
        self.max_enemy_speed = 20
        self.Loginwindowalive = None
        self.local_player = None
        pygame.init()
        self.clock = pygame.time.Clock()
        self.gameDisplay = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5050))
        self.players = []

    def display_players(self, players):
        for player in players:
            if player.car_x_coordinate and player.car_y_coordinate:
                local = False
                if player.username == self.local_player.username:
                    local = True
                    self.car(player.car_x_coordinate, player.car_y_coordinate, local)
                    self.displayUsername(player.username, player.car_x_coordinate, player.car_y_coordinate)
                    continue
                relative_y = int(player.dist_covered) - int(self.local_player.dist_covered)
                if (relative_y > 0) and relative_y < 600:
                    self.car(player.car_x_coordinate,self.local_player.car_y_coordinate-relative_y, local)
                    self.displayUsername(player.username, player.car_x_coordinate, self.local_player.car_y_coordinate-relative_y)
                elif relative_y > 600:
                    self.arrow_up(player.car_x_coordinate)
                    self.displayUsername(player.username,player.car_x_coordinate,5)
                    print("dsplayinguppp")
                elif relative_y < 0:
                    self.arrow_down(player.car_x_coordinate)
                    self.displayUsername(player.username,player.car_x_coordinate,420)
                elif relative_y == 0:
                    self.car(player.car_x_coordinate,self.local_player.car_y_coordinate, local)
                    self.displayUsername(player.username, player.car_x_coordinate, self.local_player.car_y_coordinate)


    def LoginWindow(self):
        # Create the main window

        self.LoginWindow = tk.Tk()
        self.LoginWindow.title("Joining the game")
        self.LoginWindow.geometry("270x100+500+250")  # Width x Height + X position + Y position
        self.Loginwindowalive = True
        # Create labels
        self.label_username = tk.Label(self.LoginWindow, text="Username:")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.LoginWindow)
        self.entry_username.pack()

        # Create label for displaying the result
        self.label_result = tk.Label(self.LoginWindow, text="")
        self.label_result.pack()

        # Create login button
        self.button_login = tk.Button(self.LoginWindow, text="Join", command=self.verifyusername)
        self.button_login.pack()

        # Run the main window loop
        self.LoginWindow.mainloop()

    def verifyusername(self):
        print("verify method reached")
        username = self.entry_username.get()
        msgtobesent = "Verify," + username
        self.client_socket.send(msgtobesent.encode())
        return_message = self.client_socket.recv(1024).decode()
        if return_message == "Login Successful, Joining the game":
            Client(self.Chat_IP,self.Chat_PORT,username)
            self.local_player = Player()
            self.local_player.username = username
            self.initialize()
            self.label_result.config(text="Login Successful, Joining the game", fg="green")
            self.LoginWindow.after(1500, self.racing_window)

        if return_message == "User name already exists":
            self.label_result.config(text="User name already exists", fg="red")

        if return_message == "Enter a username":
            self.label_result.config(text="Enter a username", fg="red")

    def initialize(self):
        # suuroundings inits
        self.display_width = 800
        self.display_height = 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.enemy_car_height = 100
        self.enemy_car_speed = 3
        self.min_enemy_speed = 0
        self.bg_speed = 3
        self.dummy_init = False
        random.seed(self.local_player.dist_covered)

        self.enemy_car_startx = self.enemys[self.current_enemy].x
        self.enemy_car_starty = self.local_player.dist_covered-self.enemys[self.current_enemy].at_dist
        self.bg_x1 = (self.display_width / 2) - (360 / 2)
        self.bg_x2 = (self.display_width / 2) - (360 / 2)
        self.bg_y1 = 0
        self.bg_y2 = -600
        self.local_surroundings = Surroundings()
        self.local_player.crashed = False
        self.local_car_img = pygame.image.load('.\\img\\car.png')
        self.opponent_car_img = pygame.image.load('.\\img\\oponent_car.png')
        self.arrowupimg = pygame.image.load('.\\img\\arrow_up.png')
        self.arrowdownimg = pygame.image.load('.\\img\\arrow_down.png')
        self.finish_img = pygame.image.load('.\\img\\finish.png')
        self.local_player.car_x_coordinate = (self.display_width * 0.45)
        self.local_player.car_y_coordinate = (self.display_height * 0.8)
        self.car_width = 49
        # enemy_car
        self.enemy_car = pygame.image.load('.\\img\\enemy_car_1.png')
        self.enemy_car_width = 49
        self.enemy_car_height = 100

        # Background
        self.bgImg = pygame.image.load(".\\img\\back_ground.jpg")

    def receive_data(self):
        sterilized_object = self.client_socket.recv(2048)
        received_object = pickle.loads(sterilized_object)
        if isinstance(received_object, Surroundings):
            self.local_surroundings = received_object

        elif isinstance(received_object[0], Player):
            self.players = received_object
            for player in self.players:
                if player.username == self.local_player.username:
                    self.local_player.position = player.position
        else:
            print("Not correct data type received by the Client(surroundings,players)")

    def car(self, car_x_coordinate, car_y_coordinate, islocal):
        if islocal:
            self.gameDisplay.blit(self.local_car_img, (car_x_coordinate, car_y_coordinate))
        else:
            self.gameDisplay.blit(self.opponent_car_img, (car_x_coordinate, car_y_coordinate))

    def arrow_up(self,x_coordinate):
            self.gameDisplay.blit(self.arrowupimg, (x_coordinate, 25))

    def arrow_down(self,x_coordinate):
            self.gameDisplay.blit(self.arrowdownimg, (x_coordinate, 560))


    def racing_window(self):
        if self.Loginwindowalive:
            self.Loginwindowalive = False
            self.LoginWindow.destroy()
        self.gameDisplay = pygame.display.set_mode(
            (self.display_width, self.display_height))
        pygame.display.set_caption('Car Racing Multiplayer Game')

        self.run_car()

    def run_car(self):

        while True:
            if not self.dummy_init and self.local_surroundings.game_started:
                print("localy starting")
                self.display_message("Starting", 2)
                self.dummy_init = True

            if self.local_player.crashed and self.local_surroundings.game_started:
                print("Crashed")
                self.current_enemy += 1
                self.enemy_car_starty = self.local_player.dist_covered-self.enemys[self.current_enemy].at_dist # Synchronize enemys
                self.enemy_car_startx = self.enemys[self.current_enemy].x
                self.enemy_car_speed = 3
                self.bg_speed = 3
                self.local_player.car_x_coordinate = (self.display_width * 0.45)
                self.display_message("Crashed", 2)
                self.local_player.crashed = False

            serialized_data = pickle.dumps(self.local_player)
            # Send the player object to the server
            self.client_socket.send(serialized_data)

            self.receive_data()
            self.receive_data()

            if (self.local_player.dist_covered / 100) >= self.race_distance:
                self.display_message("Finished", 7)
                self.display_finish()
                self.local_player.finished = True
                print("Race Finished")
                pygame.QUIT
                pygame.quit()
                self.client_socket.close()
                break

            if self.local_surroundings.game_started:
                self.local_player.dist_covered += self.bg_speed * 1.2
                self.enemy_car_starty += self.enemy_car_speed
                self.bg_y1 += self.bg_speed
                self.bg_y2 += self.bg_speed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client_socket.close()
                    pygame.QUIT
                    pygame.quit()
                    print("Game closed")

                if self.local_surroundings.game_started:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            if (self.enemy_car_speed < self.max_enemy_speed) and (self.bg_speed < self.max_bg_speed):
                                self.enemy_car_speed += 1
                                self.bg_speed += 1

                        if event.key == pygame.K_DOWN:
                            if (self.enemy_car_speed > self.min_enemy_speed) and (self.bg_speed > 0):
                                self.enemy_car_speed -= 1
                                self.bg_speed -= 1

                        if event.key == pygame.K_LEFT:
                            self.local_player.car_x_coordinate -= 50

                        if event.key == pygame.K_RIGHT:
                            self.local_player.car_x_coordinate += 50
            if self.bg_y1 >= self.display_height:
                self.bg_y1 = -600

            if self.bg_y2 >= self.display_height:
                self.bg_y2 = -600

            if self.enemy_car_starty > self.display_height:
                self.current_enemy += 1
                self.enemy_car_starty = self.local_player.dist_covered-self.enemys[self.current_enemy].at_dist # synchronize enemy
                self.enemy_car_startx = self.enemys[self.current_enemy].x

            self.gameDisplay.fill(self.black)
            self.back_ground_raod()

            self.run_enemy_car(self.enemy_car_startx, self.enemy_car_starty)

            if self.local_player.car_y_coordinate < self.enemy_car_starty + self.enemy_car_height:
                if self.local_player.car_x_coordinate > self.enemy_car_startx and self.local_player.car_x_coordinate < self.enemy_car_startx + self.enemy_car_width or self.local_player.car_x_coordinate + self.car_width > self.enemy_car_startx and self.local_player.car_x_coordinate + self.car_width < self.enemy_car_startx + self.enemy_car_width:
                    self.local_player.crashed = True

            if self.local_player.car_x_coordinate < 310 or self.local_player.car_x_coordinate > 460:
                self.local_player.crashed = True
            self.Distance_Coverd(self.local_player.dist_covered)
            self.Position(self.local_player.position)
            self.Speed(self.bg_speed)
            if self.local_player.dist_covered/100 >= self.race_distance-50:
                self.display_finish()
            self.RaceDistance()
            self.display_players(self.players)
            if not self.local_surroundings.game_started:
                self.wait_for_others()
            pygame.display.update()
            self.clock.tick(60)

    def display_message(self, msg,time):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        self.gameDisplay.blit(text, (400 - text.get_width() // 2, 240 - text.get_height() // 2))
        #self.display_credit()
        pygame.display.update()
        self.clock.tick(60)
        sleep(time)
        #pygame.QUIT
        #pygame.quit()
        #self.client_socket.close()

    def back_ground_raod(self):
        self.gameDisplay.blit(self.bgImg, (self.bg_x1, self.bg_y1))
        self.gameDisplay.blit(self.bgImg, (self.bg_x2, self.bg_y2))

    def run_enemy_car(self, thingx, thingy):
        self.gameDisplay.blit(self.enemy_car, (thingx, thingy))

    def Distance_Coverd(self, distance):
        distance = int(distance/100)
        if distance > 500:
            distance = 500
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Distance covered:" + str(distance), True, self.white)
        self.gameDisplay.blit(text, (0, 0))

    def RaceDistance(self):
        dist = self.race_distance
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Race distance:" + str(dist), True, self.white)
        self.gameDisplay.blit(text, (0, 25))

    def Speed(self, Speed):
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Speed:" + str(Speed), True, self.white)
        self.gameDisplay.blit(text, (0, 50))

    def Position(self,position):
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Position:" + str(position), True, self.white)
        self.gameDisplay.blit(text, (0, 75))

    def wait_for_others(self):
        font = pygame.font.SysFont("arial", 30)
        text = font.render("Waiting ", True, self.white)
        self.gameDisplay.blit(text, (10, 200))
        text = font.render("for ", True, self.white)
        self.gameDisplay.blit(text, (10, 240))
        text = font.render("opponents ", True, self.white)
        self.gameDisplay.blit(text, (10, 280))

    def display_finish(self):
        relative_y = int(self.race_distance*100 - self.local_player.dist_covered)
        if (relative_y > 0) and relative_y < 600:
            print("x,y", (self.display_width / 2) - (360 / 2), self.local_player.car_y_coordinate - relative_y)
            self.gameDisplay.blit(self.finish_img, ((self.display_width / 2) - (360 / 2), self.local_player.car_y_coordinate - relative_y))

    def Starting(self):
        font = pygame.font.SysFont("arial", 30)
        text = font.render("Game Starting", True, self.white)
        self.gameDisplay.blit(text, (10, 200))
        sleep(2)

    def displayUsername(self, username, x, y):
        font = pygame.font.SysFont("arial", 20)
        text = font.render(username, True, self.red)
        self.gameDisplay.blit(text, (x, y + self.enemy_car_height))

    def display_credit(self):
        font = pygame.font.SysFont("lucidaconsole", 14)
        text = font.render("Thanks for playing!", True, self.white)
        self.gameDisplay.blit(text, (600, 520))


if __name__ == '__main__':
    car_racing = CarRacing()
    car_racing.LoginWindow()
