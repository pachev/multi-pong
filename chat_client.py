import sys
import socket
import select

HOST = ''
PORT = 2129
RECV_BUFFER = 1024


def chat_client():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)

    try:
        client_socket.connect((HOST, PORT))
    except:
        print("Unable to connect")
        sys.exit()

    print("Connected to remote host. You can start sending messages")
    sys.stdout.write('[Me] '); sys.stdout.flush()

    while True:
        socket_list = [sys.stdin, client_socket]

        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
        for sock in ready_to_read:
            if sock == client_socket:
                data = sock.recv(RECV_BUFFER).decode()
                if not data:
                    print("Nothing sent...")
                    sys.exit()
                else:
                    # print data
                    sys.stdout.write(data)
                    sys.stdout.write('[Me] ')
                    sys.stdout.flush()

            else:
                # user entered a message
                msg = sys.stdin.readline()
                client_socket.send(msg.encode())
                sys.stdout.write('[Me] '); sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(chat_client())