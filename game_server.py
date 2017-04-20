# Game Server

import sys

from _thread import *
from pygame import time as gametime

import json
import random
import select
import socket
from pygame.locals import Rect
from server.ball import Pong
import data.constants as const

REMOTE_CLIENTS = []
REMOTE_PLAYERS = []

USERNAMES = [
    "TalkativeLug",
    "FaithfulWeirdo",
    "MeagerSucker",
    "ForthrightNerd",
    "ElderlyCheater",
    "RadiantJerk",
    "MediocreNobody",
    "HandmadeDeadbeat",
    "RapidSicko",
    "UnequalFool"
]


class Player:

    global USERNAMES

    def __init__(self, player):
        self.id = player
        self.y = int(const.SCREENSIZE[1]*0.5)
        self.side = player % 2

        self.height = 100
        self.width = 10

        if self.side == 0:
            self.x = const.SCREENSIZE[0] - (5 + (player * 30))
        else:
            self.x = (player * 30) + 5 if player > 1 else 5

        self.rect = Rect(0, self.y-int(self.height*0.5), self.width, self.height)

        self.color = random_color()
        self.name = random.choice(USERNAMES)
                
    def update(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.rect.center = (self.x, self.y)

    def get_info(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "side": self.side,
            "color": self.color,
            "name": self.name
        }


def random_color():
    rgb = []
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb.append(r)
    rgb.append(g)
    rgb.append(b)
    return tuple(rgb)


# Function to broadcast to all other players besides the server and current client
def broadcast_all(sock, info):
    global REMOTE_CLIENTS

    for socket in REMOTE_CLIENTS[1:]:
        if socket != sock:
            try:
                socket.sendall(info)
            except:
                socket.close()
                i = REMOTE_CLIENTS.index(socket)
                p = REMOTE_PLAYERS[i-1]
                print("removing player", p.id, "from list")
                REMOTE_CLIENTS.remove(socket)
                REMOTE_PLAYERS.remove(p)


def broadcast_global(info):
    global REMOTE_CLIENTS

    for socket in REMOTE_CLIENTS[1:]:
        try:
            socket.sendall(info)
        except:
            print("error broadcast_global")
            socket.close()
            i = REMOTE_CLIENTS.index(socket)
            p = REMOTE_PLAYERS[i-1]
            print("removing player", p.id, "from list")
            REMOTE_CLIENTS.remove(socket)
            REMOTE_PLAYERS.remove(p)


# Updates the location of the player and lets the other players know
def udp_to_tcp_update(location, type):
    global REMOTE_PLAYERS
    if "updateLocation" in type:
        player = next((player for player in REMOTE_PLAYERS if player.get_info()["id"] == location["id"]))
        player.update(location["x"], location["y"])
        info = type + json.dumps(player.get_info()) +";\r\n"
        broadcast_global(info.encode())
    else:
        broadcast_global((type + json.dumps(location) + ";\r\n").encode())


def handle_udp(sock):

    while True:
        data, addr = sock.recvfrom(const.RECV_BUFF) # buffer size is 1024 bytes
        msg = data.decode().split(";")
        if msg[0] == "updateLocation":
            udp_to_tcp_update(json.loads(msg[1]), msg[0]+";\r\n")
        elif msg[0] == "updateBallLocation":
            udp_to_tcp_update(json.loads(msg[1]), msg[0]+";\r\n")


def handle_ball(ball):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clock = gametime.Clock()

    while True:
        global REMOTE_PLAYERS
        ball.update(REMOTE_PLAYERS)
        info = "updateBallLocation;" + json.dumps(ball.get_info()) +";\r\n"
        broadcast_global(info.encode())
        clock.tick(const.FPS)


def main():

    global REMOTE_CLIENTS
    global REMOTE_PLAYERS

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    REMOTE_CLIENTS.append(s)
     
    # Bind socket to local host and port
    try:
        udp_server.bind((const.HOST, const.PORT))
        s.bind((const.HOST, const.PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
         
    # TODO: This has to change in case gameserver is ran seperately from PingPong
    ball = Pong(const.SCREENSIZE, 1)
    
    start_new_thread(handle_udp, (udp_server, ))
    start_new_thread(handle_ball, (ball, ))
     
    # Start listening on socket
    s.listen(5)

    print("server has started and listening")

    while True:
        try: 
            ready_read, ready_write, in_error = select.select(REMOTE_CLIENTS, [], [], 0)
            for sock in ready_read:

                # new connection received here
                if sock == s:
                    conn, addr = s.accept()
                    print("Client", addr[0], "connected on", addr[1])

                    player = Player(len(REMOTE_CLIENTS)-1)  # don't count the main server socket

                    print("player created and added to list")
                    package = json.dumps([player.get_info(), ball.get_info()])
                    conn.sendall(package.encode())

                    REMOTE_PLAYERS.append(player)
                    REMOTE_CLIENTS.append(conn)
                    print("initial player sent")
                    broadcast_all(conn,("newPlayer;"+ json.dumps(player.get_info()) +";\r\n").encode())

                    cur_list = [player.get_info() for player in REMOTE_PLAYERS]
                    broadcast_global(("currentList;"+ json.dumps(cur_list) + ";\r\n").encode())
                # else it's an update message from a client
                else:
                    try:
                        data = sock.recv(const.RECV_BUFF)
                        if data:
                            res = data.decode().split(";")
                            if res[0] == "combo":
                                print("received: ",res[1])
                            elif res[0] == "sentMessage":
                                msg = "receivedMessage;" + res[1] + ';' + res[2]+';\r\n'
                                broadcast_all(sock,msg.encode())
                        else:
                            # handles the case where our client has los a connection
                            sock.close()

                            i = REMOTE_CLIENTS.index(sock)
                            p = REMOTE_PLAYERS[i-1]

                            print("removing player", p.id, "from list")
                            broadcast_global(("removePlayer;"+ json.dumps(p.get_info()) + ";\r\n").encode())

                            REMOTE_PLAYERS.remove(p)
                            REMOTE_CLIENTS.remove(sock)
                    except:
                        print("data not received")
                        continue

        except KeyboardInterrupt:

            print("Closing server")
            for sock in REMOTE_CLIENTS:
                sock.close()
            sys.exit(0)
 
# TODO: Add other means of closing the server.
if __name__=='__main__':
        main()
