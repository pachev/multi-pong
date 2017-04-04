# Game Server

import socket
import sys
from _thread import *
 
HOST = ''   
PORT = 2116
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print ('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print ('Socket bind complete')
 
#Start listening on socket
s.listen(5)

print ('Socket now listening For Clients')
 
#Function for handling connections. 
def handleclient(conn):

    #Sending message to connected client
    conn.send(b'Welcome to the server. Type something and hit enter\r\n') 
     
    #TODO: Main logic in here will send player packets
    while True:
        msg = conn.recv(1024).decode()
        reply = b'OK...\r\n' 
        print(msg)
        if not msg or "quit" in msg: 
            break
     
        conn.send(reply)
     
    #came out of loop
    conn.close()
 

while True:
    try: 
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print ('Connected with ' + addr[0] + ':' + str(addr[1]))

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        #this function also automatically closes the thread once the function has ened. Part of python library
        start_new_thread(handleclient ,(conn,))
    except KeyboardInterrupt:
        print("Closing server")
        s.close()
        sys.exit(0);
 
#TODO: Add other means of closing the server. 
