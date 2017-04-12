## Forked from https://github.com/smoross/Pygame 
## a game from Samantha Moross

import pygame
import sys, os, time
import random
import json

from pygame.locals import Rect, DOUBLEBUF, QUIT, K_ESCAPE, KEYDOWN, K_DOWN, \
    K_LEFT, K_UP, K_RIGHT, KEYUP, K_LCTRL, K_RETURN, FULLSCREEN

## Networking imports
from socket import *
from _thread import *

## Local game imports
from paddle import PlayerPaddle


HOST = ''
GAME_PORT = 2115
CHAT_PORT = 2129
BALL_PORT = 2116

# Initialize the game
pygame.init()

screen_width = 680
screen_length = 620

screensize = (screen_width, screen_length)

# Set the screen
screen = pygame.display.set_mode(screensize)

chat_screen_length = 200
pong_screen_length = screen_length-chat_screen_length

pong_screensize = (screen_width, pong_screen_length)
chat_screensize = (screen_width, chat_screen_length)

FPS = 200

PLAYER_LIST = []
RECV_BUFF = 1024

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 100, 00)
red = (255, 0, 0)

class Pong(object):
    def __init__(self, screensize, id, x, y, lscore, rscore):
        self.screensize = screensize
        self.id = id
        self.centerx = x
        self.centery = y
        self.lscore = lscore
        self.rscore = rscore
        self.radius = 8

        # create shape and sizes it
        self.rect = pygame.Rect(self.centerx-self.radius, 
                                self.centery-self.radius,
                                self.radius*2, self.radius*2)
        self.color = white

    def update(self, x, y, lscore, rscore):
        self.centerx = x
        self.centery = y
        self.lscore = lscore
        self.rscore = rscore
        self.rect.center = (self.centerx, self.centery)

    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 0)
        # creates black outline of the circle
        pygame.draw.circle(screen, black, self.rect.center, self.radius, 1)

def update_players(p_list):
    global PLAYER_LIST

    pids = [p.id for p in PLAYER_LIST]
    for p in p_list:
        if p["id"] not in pids:
            PLAYER_LIST.append(PlayerPaddle(screensize, p["id"], p["color"]))

def handle_ball(server, pong):
    global RECV_BUFF

    while True:
        data, addr = server.recvfrom(RECV_BUFF) # buffer size is 1024 bytes
        msg = data.decode().split(";")
        print('msg', msg)
        if msg[0] == "updateLocation":
            print("located")
        elif msg[0] == "updateBallLocation":
            try:
                detail = json.loads(msg[1])
                pong.update(
                    detail["x"],
                    detail["y"],
                    detail["lscore"],
                    detail["rscore"],
                )
            except:
                print("ball error", msg)


def handle_server(server, pong):
    global PLAYER_LIST
    data = b'ack;\r\n'

    while True:
        msg = server.recv(RECV_BUFF).decode().split(";")

        if msg[0] == "newPlayer":
            try:
                server.sendall(data)
                detail = json.loads(msg[1])
                player = PlayerPaddle(screensize, detail["id"], detail["color"])
                PLAYER_LIST.append(player)
            except:
                print("new player could not be created:", msg)
        if msg[0] == "currentList":
            try:
                print("received list: ", msg[1])
                server.sendall(data)
                p_list = json.loads(msg[1])
                update_players(p_list)
            except:
                print("current list could not be read:", msg)
        elif msg[0] == "updateLocation":
            try:
                server.sendall(data)
                detail = json.loads(msg[1])
                player = next((player for player in PLAYER_LIST if player.getId() == detail["id"]))
                player.update_local(detail["y"])
            except:
                print("something went wrong with msg", msg)
        elif msg[0] == "removePlayer":
            try:
                server.sendall(data)
                detail = json.loads(msg[1])
                player = next((player for player in PLAYER_LIST if player.getId() == detail["id"]))
                PLAYER_LIST.remove(player)
            except:
                print("could not remove stupid player")
        elif msg[0] == "updateBallLocation":
            try:
                server.sendall(data)
                detail = json.loads(msg[1])
                pong.update(
                    detail["x"],
                    detail["y"],
                    detail["lscore"],
                    detail["rscore"],
                )
            except Exception as e:
                print("ball error", e)

    server.close()


def main():
    global PLAYER_LIST
    global RECV_BUFF

    # TODO: get host and port from a config file and possibly from settings
    server = socket(AF_INET, SOCK_STREAM)

    #player socket stream: To change later
    udp_server = socket(AF_INET, SOCK_DGRAM)
    # ball socket stream: may remain
    ball_server = socket(AF_INET, SOCK_DGRAM)

    try:
        server.connect((HOST, GAME_PORT))
        # ball_server.bind((HOST,BALL_PORT))
    except error as msg:
        print("Could not connect to server", msg)
        sys.exit(1)


    '''
    Grabs a player from server instead of creating indiviudally
    Upon initial connection the server creates a player with an id and sends this to the server. 
    it's the first response and lets the new client know their client id
    '''
    res = json.loads(server.recv(RECV_BUFF).decode())
    player_id = res[0]["id"] 
    play_color = res[0]["color"]
    data = b'ack;\r\n'
    server.sendall(data)

    print("Loaded new player from server with id:", player_id)

    # This start_new_therad function starts a thread and automatically closes it when the function is done
    running = True

    clock = pygame.time.Clock()
    pong = Pong(
        pong_screensize, 
        res[1]["id"],
        res[1]["x"],
        res[1]["y"],
        res[1]["lscore"],
        res[1]["rscore"],
    )

    player_paddle1 = PlayerPaddle(pong_screensize, player_id, play_color)
    PLAYER_LIST.append(player_paddle1)

    print("player:", player_id, "created and added")

    pygame.display.set_caption('Pong')

    pygame.mixer.music.load(os.path.join('data/ping.wav'))
    pygame.mixer.music.load(os.path.join('data/win.wav'))
    pygame.mixer.music.load(os.path.join('data/lose.wav'))

    win = pygame.mixer.Sound(os.path.join('data/win.wav'))
    lose = pygame.mixer.Sound(os.path.join('data/lose.wav'))        

    start_new_thread(handle_server , (server,pong))

    while running: # Main game loop
        if len(PLAYER_LIST) <= 1:
            continue
        else:
            for event in pygame.event.get(): # handles events
                if event.type == pygame.QUIT: # Makes sure we can quit the game
                        pygame.quit()
                        exit()

                if event.type == KEYDOWN:
                        if event.key == K_UP:
                                player_paddle1.direction = -1
                        elif event.key == K_DOWN:
                                player_paddle1.direction = 1

                if event.type == KEYUP: 
                        if event.key == K_UP and player_paddle1.direction == -1:
                                player_paddle1.direction = 0 

                        elif event.key == K_DOWN and player_paddle1.direction == 1:
                                player_paddle1.direction = 0

            player_paddle1.update(udp_server)

            screen.fill(green)
            # draw vertical line for ping pong design
            pygame.draw.line(screen, white, (screen_width/2, 0), (screen_width/2, pong_screen_length), 5)

            # draw horizontal line to divide the pong game from the chat
            pygame.draw.line(screen, white, (0, pong_screen_length), (screen_width, pong_screen_length), 5)

            # draw rectangle for the chat
            pygame.draw.rect(screen, black, (0, pong_screen_length, screen_width, chat_screen_length), 0)

            for player in PLAYER_LIST:
                player.render(screen)

            pong.render(screen) # calls render function to the screen

            default_font = pygame.font.get_default_font()
            font = pygame.font.Font(default_font, 50)
            msg = font.render("   "+str(pong.lscore)+"  Score  "+str(pong.rscore), True, white)
            screen.blit(msg, (320, 0)) # adds score to the screen

            clock.tick(FPS)
            pygame.display.flip() # renders everything based on the update

    pygame.display.flip() 
    server.close()
    pygame.time.delay(5000)
    pygame.quit()

if __name__ == '__main__':
        main()
