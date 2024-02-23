import socket
import threading
from socket import *

#First example for TestServer1
print('We are using the server to capatalisze a sentence sent in from the client, and then sending this result back to the client using web socket programming.')

#Define variables
HEADER = 64     #Header of 64 bytes for the first msg
CONNECTIONPORT = 12000
DATAPORT = 5000
FORMAT = 'utf-8'
DISCONNECT_PROTOCOL = "!DISCONNECT"
SERVER_NAME = "Server"

#Handles the threading of each client connection running at the same time so the server can receive ina parallel way
def handle_client(connectionSocket,addr):       
    print(f"[NEW CONNECTION] {addr} connected")
    
    #TO:DO send new port number here, because the UDP socket isn't receiving properly
    #The UDP socket probably shouldn't be here and I'm sure I can resolve that when
    #The send/receive protocol is done and the new port is sent
    
    #Create a new UDP socket with a new port for each connected client
    dataSocket = socket(AF_INET,SOCK_DGRAM)
    dataSocket.bind(('', DATAPORT))
    connected = True
    while connected:
        msg,clientAddress = dataSocket.recvfrom(2048)
        print(msg)
        if msg:      #Check if valid message      
            print('we do have a valid message')      
            if msg == DISCONNECT_PROTOCOL:
                connected = False
            capitalizedSentence = msg.upper() 
            dataSocket.sendto(capitalizedSentence.encode(FORMAT),clientAddress)
    
    dataSocket.close()
    connectionSocket.close()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-2}")


def start_server():
    serverSocket = socket(AF_INET,SOCK_STREAM) 
    serverSocket.bind(("",CONNECTIONPORT)) #Connect with TCP socket
    serverSocket.listen(1)
    print(f"[LISTENING] Server is listening on {CONNECTIONPORT}")
    print('The server is ready to recieve client connection requests')
    while True:
        connectionSocket, addr = serverSocket.accept()  #TCP connection stays open for new clients
        thread = threading.Thread(target=handle_client, args=(connectionSocket,addr))
        thread.start()
        # -1 to exclude server thread
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")
        


start_server()
