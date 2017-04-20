## Forked from https://github.com/smoross/Pygame 
## a game from Samantha Moross
import json
import tkinter as tk
from _thread import *
from socket import *
from tkinter import *
import os

import pygame
from pygame.locals import KEYDOWN, K_DOWN, \
    K_UP, KEYUP

from client.ball import Pong
from client.chatbox import *
from client.paddle import PlayerPaddle
import data.constants as const

# Initialize the game
PLAYER_LIST = []

window = tk.Tk()

window.geometry('340x620+680+0')
window.title("Pong Chat")

pygame.init()
    
# Set the screen

screen = pygame.display.set_mode(const.SCREENSIZE)
chat_box = Chatbox(window)


def update_players(p_list):
    global PLAYER_LIST

    pids = [p.id for p in PLAYER_LIST]
    for p in p_list:
        if p["id"] not in pids:
            PLAYER_LIST.append(PlayerPaddle(const.SCREENSIZE, p["id"], p["color"]))


def handle_ball(server, pong):

    while True:
        data, addr = server.recvfrom(const.RECV_BUFF) # buffer size is 1024 bytes
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


def handle_server(queue, server, pong):
    global screen
    global PLAYER_LIST
    data = b'ack;\r\n'

    while True:
        msg = server.recv(const.RECV_BUFF).decode().split(";")

        if msg[0] == "newPlayer":
            try:
                detail = json.loads(msg[1])
                player = PlayerPaddle(const.SCREENSIZE, detail["id"], detail["color"])
                PLAYER_LIST.append(player)
                queue.append(["SERVER", "New player " + detail["name"] + " has arrived."])
            except:
                print("new player could not be created:", msg)
        if msg[0] == "currentList":
            try:
                print("received list: ", msg[1])
                p_list = json.loads(msg[1])
                update_players(p_list)
            except:
                print("current list could not be read:", msg)
        elif msg[0] == "updateLocation":
            try:
                detail = json.loads(msg[1])
                player = next((player for player in PLAYER_LIST if player.get_id() == detail["id"]))
                player.update_local(detail["y"])
            except:
                print("something went wrong with msg", msg)
        elif msg[0] == "removePlayer":
            try:
                detail = json.loads(msg[1])
                player = next((player for player in PLAYER_LIST if player.get_id() == detail["id"]))
                PLAYER_LIST.remove(player)
            except:
                print("could not remove stupid player")
        elif msg[0] == "updateBallLocation":
            try:
                detail = json.loads(msg[1])
                pong.update(
                    detail["x"],
                    detail["y"],
                    detail["lscore"],
                    detail["rscore"],
                )
            except Exception as e:
                print("ball error", e)
        elif msg[0] == "receivedMessage":
            global chat_box
            try:
                # Appends the message to the queue in main thread to avoid tkinter threadign error
                queue.append([msg[1], msg[2]])
            except Exception as e:
                print("Chat Error", e)

    server.close()


def main():
    global PLAYER_LIST
    global chat_box
    global screen
    msg_queue = []

    # TODO: get host and port from a config file and possibly from settings
    server = socket(AF_INET, SOCK_STREAM)

    udp_server = socket(AF_INET, SOCK_DGRAM)

    try:
        server.connect((const.HOST, const.PORT))
    except error as msg:
        print("Could not connect to server", msg)
        sys.exit(1)


    '''
    Grabs a player from server instead of creating individually
    Upon initial connection the server creates a player with an id and sends this to the server. 
    it's the first response and lets the new client know their client id
    '''
    res = json.loads(server.recv(const.RECV_BUFF).decode())
    player_id = res[0]["id"] 
    player_color = res[0]["color"]
    player_name = res[0]["name"]
    data = b'ack;\r\n'
    server.sendall(data)

    print("Loaded new player from server with id:", player_id)

    def command(txt):
        print(txt)
        msg = 'sentMessage;' + player_name + ';' + txt + ';\r\n'
        server.sendall(msg.encode())

    # This start_new_thread function starts a thread and automatically closes it when the function is done
    running = True

    clock = pygame.time.Clock()
    pong = Pong(
        const.SCREENSIZE,
        res[1]["id"],
        res[1]["x"],
        res[1]["y"],
        res[1]["lscore"],
        res[1]["rscore"],
    )

    player_paddle1 = PlayerPaddle(const.SCREENSIZE, player_id, player_color)
    PLAYER_LIST.append(player_paddle1)

    print("player:", player_id, "created and added")

    pygame.display.set_caption('Multi Pong')

    pygame.mixer.music.load(os.path.join('data/ping.wav'))
    pygame.mixer.music.load(os.path.join('data/win.wav'))
    pygame.mixer.music.load(os.path.join('data/lose.wav'))

    win = pygame.mixer.Sound(os.path.join('data/win.wav'))
    lose = pygame.mixer.Sound(os.path.join('data/lose.wav'))        

    start_new_thread(handle_server, (msg_queue,server, pong))

    chat_box.set_nick("SERVER")
    
    chat_box.set_command(command)

    chat_box.send("Welcome to Pong! Your username has been set to - " + player_name + ". Deal with it.")
    chat_box.send("Waiting for players to connect...")

    chat_box.set_nick(player_name)

    while running:  # Main game loop
        if len(PLAYER_LIST) <= 0:
            continue
        else:
            for event in pygame.event.get():  # handles events
                if event.type == pygame.QUIT:  # Makes sure we can quit the game
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

            screen.fill(const.GREEN)
            # draw vertical line for ping pong design
            pygame.draw.line(screen, const.WHITE, (const.SCREEN_WIDTH / 2, 0), (const.SCREEN_WIDTH / 2, const.SCREEN_LENGTH), 5)

            for player in PLAYER_LIST:
                player.render(screen)

            pong.render(screen)  # calls render function to the screen

            default_font = pygame.font.get_default_font()
            font = pygame.font.Font(default_font, 50)

            msg = font.render("   " + str(pong.lscore) + "  Score  " + str(pong.rscore), True, const.WHITE)
            screen.blit(msg, (320, 0))  # adds score to the screen

            for msg in msg_queue:
                chat_box.user_message(msg[0], msg[1])
                msg_queue.remove(msg)

            chat_box.interior.pack(expand=True, fill=BOTH)
            
            window.update()

            clock.tick(const.FPS)
            pygame.display.flip()  # renders everything based on the update

    pygame.display.flip() 
    server.close()
    pygame.time.delay(5000)
    pygame.quit()

if __name__ == '__main__':
        main()
