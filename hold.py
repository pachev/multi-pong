# connecting to server logic
def handle_server(server):
    while True:
        data = b"('score': 0, 'player': 1, 'x_pos': 30, 'y_pos': 20)"
        server.send(data)
        data = server.recv(1024).decode()
        print(data)

    server.close()
#TODO: get host and port from a config file and possibly from settings
server = socket(AF_INET, SOCK_STREAM)
server.connect(('', 2115))
start_new_thread(handle_server ,(server,))
