import sys
import socket
import select
import random

# Global Constants
HOST = ''
PORT = 2129
SOCKET_LIST = []
RECV_BUFFER = 1024
RANDOM_USERNAMES = [
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
ACTIVE_USERS = []


class User:
    def __init__(self, user, addr):
        self.user = user
        self.name = random.choice(RANDOM_USERNAMES)
        self.addr = addr
        RANDOM_USERNAMES.remove(self.name)

    def get_name(self):
        return self.name

    def get_user(self):
        return self.user

    def get_addr(self):
        return self.addr


def chat_server():

    global SOCKET_LIST
    global RANDOM_USERNAMES

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(15)

    SOCKET_LIST.append(server_socket)

    print("Chat server started on port " + str(PORT))

    while True:
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:

            print("sock")
            print(sock)

            # If a new connection request is received
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)

                user = User(sockfd, addr)
                username = user.get_name()

                ACTIVE_USERS.append(user)

                print("[" + username + "] connected")
                print("Client (%s, %s) connected" % user.get_addr())
                sockfd.send(username.encode())
                broadcast(server_socket, sockfd, "\n[" + username + "] entered the PONG game chat room!\n")

            # A message is received from the client (not a new connection)
            else:
                try:
                    data = sock.recv(RECV_BUFFER).decode()
                    for user in ACTIVE_USERS:
                        if user.get_user() == sock:
                            username = user.get_name()
                            break
                    if data:
                        broadcast(server_socket, sock, "\r" + '[' + username + '] ' + data)
                    else:
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                            RANDOM_USERNAMES.add(username)
                            print("Client [" + username + "] removed from list")

                        broadcast(server_socket, sock, "\n[" + username + "] is offline\n")

                except:
                    broadcast(server_socket, sock, "\n[" + username + "] is offline\n")
                    continue

    server_socket.close()


def broadcast(server_socket, sock, message):
    global SOCKET_LIST

    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock:
            try:
                socket.send(message.encode())
            except:
                # broken socket connection, close it  and remove it
                socket.close()

                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)


if __name__ == "__main__":
    sys.exit(chat_server())