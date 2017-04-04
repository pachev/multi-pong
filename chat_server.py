import sys
import socket
import select

# Global Constants
HOST = ''
PORT = 2129
SOCKET_LIST = []
RECV_BUFFER = 1024


def chat_server():

    global SOCKET_LIST

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(15)

    SOCKET_LIST.append(server_socket)

    print("Chat server started on port " + str(PORT))

    while True:
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:

            # If a new connection request is received
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print("Client (%s, %s) connected" % addr)
                broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)

            # A message is received from the client (not a new connection)
            else:
                try:
                    data = sock.recv(RECV_BUFFER).decode()
                    if data:
                        broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)
                    else:
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)

                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
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