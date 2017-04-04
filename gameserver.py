# Game Server

import socket, select
import json
import sys
from _thread import *

REMOTE_CLIENTS = []
REMOTE_PLAYERS = []

HOST = ''   
PORT = 2115
 
class Player:
    def __init__(self, player):
        self.player = player
        self.centerx= 0
        self.centery = 0
        # Add random colors here to differentiate players
        self.color = 'white'
                
    def update(self, x, y):
        self.centerx = x
        self.centery = y

    def get_info(self):
        info = {}
        info["id"] = self.player
        info["x"] = self.centerx
        info["y"] = self.centery
        return info

#Function to boradcast to all other players besides the server and current client
def broadcast_all(serv_sock, sock,info):
    global REMOTE_CLIENTS

    for socket in REMOTE_CLIENTS:
        if socket != sock and socket != serv_sock:
            try:
                socket.sendall(info)
            except:
                socket.close()
                REMOTE_CLIENTS.remove(socket)

 

def main():
     
    global HOST
    global PORT
    global REMOTE_CLIENTS

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    REMOTE_CLIENTS.append(s)
     
    #Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
         
     
    #Start listening on socket
    s.listen(5)
    print("server has started and listening")



    while True:
        try: 
            ready_read, ready_write, in_erro = select.select(REMOTE_CLIENTS, [], [], 0)
            for sock in ready_read:
                #new connection received here
                if sock == s:
                    conn, addr = s.accept()
                    REMOTE_CLIENTS.append(conn)
                    print ("Client", addr[0], "connected on", addr[1])

                    player = Player(len(REMOTE_CLIENTS)-1)
                    REMOTE_PLAYERS.append(player)
                    broadcast_all(s,conn,("newPlayer;"+ json.dumps(player.get_info())).encode())
                #else it's an update message from a client
                else:
                    try:
                        data = sock.recv(1024)
                        if data:
                            broadcast_all(s, sock, data)
                        else:
                            #handles the case where our client has los a connection
                            sock.close()
                            print("removing", sock.getsockname, "from list")
                            REMOTE_CLIENTS.remove(sock)
                    except:
                        broadcast_all(s, sock, "something went wrong")
        except KeyboardInterrupt:
            print("Closing server")
            for sock in REMOTE_CLIENTS:
                sock.close()
            sys.exit(0);
 
#TODO: Add other means of closing the server. 
if __name__=='__main__':
        main()
