import socket
import threading
from socket import *

#First example for TestServer1
print('We are using the server to capatalisze a sentence sent in from the client, and then sending this result back to the client using web socket programming.')

#Define variables
HEADER = 64     #Header of 64 bytes for the first msg
PORT = 12000
FORMAT = 'utf-8'
DISCONNECT_PROTOCOL = "!DISCONNECT"


#Part 1
#Connect with TCP socket
#TCP connection stays open for new clients

#Handles the threading of each client connection running at the same time so the server can receive ina parallel way
def handle_client(connectionSocket,addr):       
    print(f"[NEW CONNECTIONS] {addr} connected")
    connected = True
    while connected:
        msg_length = connectionSocket.recv(HEADER).decode(FORMAT) 
        if msg_length:      #Check if valid message
            print(msg_length)
            msg_length = int(msg_length)
            msg = connectionSocket.recv(msg_length).decode(FORMAT)
            
            if msg == DISCONNECT_PROTOCOL:
                connected = False
            capitalizedSentence = msg.upper() 
            connectionSocket.send(capitalizedSentence.encode(FORMAT))
    
    connectionSocket.close()
        

def start_server():
    serverPort = PORT
    serverSocket = socket(AF_INET,SOCK_STREAM) 
    serverSocket.bind(("",serverPort)) 
    serverSocket.listen(1)
    print(f"[LISTENING] Server is listening on {PORT}")
    print('The server is ready to recieve client connection requests')
    while True:
        connectionSocket, addr = serverSocket.accept()
        thread = threading.Thread(target=handle_client, args=(connectionSocket,addr))
        thread.start()
        # -1 to exclude server thread
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")
        


start_server()
#Part 2
#Create a new UDP socket with a new port for each connected client
#Data is transferred here