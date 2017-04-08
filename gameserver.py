# Game Server
#TODO: remove player from room after the quit
#


import random
import socket, select
import json
import sys
from _thread import *

REMOTE_CLIENTS = []
REMOTE_PLAYERS = []
RECV_BUFF = 1024
COLORS = [
    (78, 103, 142), 
    (142, 101, 78),
    (198, 101, 182),
    (101, 198, 197),
    (244, 230, 73),
    (178, 41, 23),
    (247, 187, 113),
    (185, 255, 173),
    (17, 67, 84),
    (244, 168, 176)
]

HOST = '0.0.0.0'
PORT = 2115
 
class Player:
    def __init__(self, player):
        global COLORS
        self.id = player
        self.x= 0
        self.y = 0
        # Add random colors here to differentiate players
        self.color = random.choice(COLORS)
        COLORS.remove(self.color)
                
    def update(self, x, y):
        self.x = x
        self.y = y

    def get_info(self):
        return self.__dict__


#Function to boradcast to all other players besides the server and current client
def broadcast_all(sock,info):
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


#Updates the location of the player and lets the other players know
def udp_to_tcp_update(location, type):
    global REMOTE_PLAYERS
    if type == "updateLocation":
        player = next((player for player in REMOTE_PLAYERS if player.get_info()["id"] == location["id"]))
        player.update(location["x"], location["y"])
    else:
        broadcast_global((type + json.dumps(location) + ";\r\n").encode())


def handle_udp(sock):
    global RECV_BUFF

    while True:
        data, addr = sock.recvfrom(RECV_BUFF) # buffer size is 1024 bytes
        msg = data.decode().split(";")
        if msg[0] == "updateLocation":
            udp_to_tcp_update(json.loads(msg[1]), msg[0]+";\r\n")
        elif msg[0] == "updateBallLocation":
            udp_to_tcp_update(json.loads(msg[1]), msg[0]+";\r\n")



def main():
     
    global HOST
    global PORT
    global RECV_BUFF
    global REMOTE_CLIENTS
    global REMOTE_PLAYERS

    #So far it's just one ball, this keeps track of it
    ball = Player(1);

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    REMOTE_CLIENTS.append(s)
     
    #Bind socket to local host and port
    try:
        udp_server.bind((HOST,PORT))
        s.bind((HOST, PORT))
    except socket.error as msg:
        print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
         
    
    start_new_thread(handle_udp, (udp_server, ))
     
    #Start listening on socket
    s.listen(5)
    print("server has started and listening")


    while True:
        try: 
            ready_read, ready_write, in_error = select.select(REMOTE_CLIENTS, [], [], 0)
            for sock in ready_read:
                #new connection received here
                if sock == s:
                    conn, addr = s.accept()
                    print ("Client", addr[0], "connected on", addr[1])
                    

                    player = Player(len(REMOTE_CLIENTS)-1) #don't count the main server socket
                    REMOTE_PLAYERS.append(player)
                    REMOTE_CLIENTS.append(conn)

                    print("player created and added to list")
                    conn.send(json.dumps(player.get_info()).encode())
                    print("initial player sent")
                    broadcast_all(conn,("newPlayer;"+ json.dumps(player.get_info()) +";\r\n").encode())

                    cur_list = [player.get_info() for player in REMOTE_PLAYERS]
                    broadcast_global(("currentList;"+ json.dumps(cur_list) + ";\r\n").encode())
                #else it's an update message from a client
                else:
                    try:
                        data = sock.recv(RECV_BUFF)
                        if data:
                            res = data.decode().split(";")
                            if res[0] == "combo;":
                                print ("received: ",res[1])
                        else:
                            #handles the case where our client has los a connection
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
            sys.exit(0);
 
#TODO: Add other means of closing the server. 
if __name__=='__main__':
        main()
