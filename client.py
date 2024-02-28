from socket import *
import threading
DISCONNECT_PROTOCOL = "/disconnect"
FORMAT = 'utf-8'
TCPPORT = 12000
ownClientPort = 13000     #for now
ownClientName = ''
serverIP = gethostbyname(gethostname())

def receive_texts(udpSocket,otherName,myName):
    while True: #Controls termination of a client to client messaging
        clientMessage, address = udpSocket.recvfrom(1024)
        if clientMessage.decode(FORMAT) == DISCONNECT_PROTOCOL:
            print(otherName,'has left the chat. You might want to disconnect yourself.')
            break
        else:
            print(myName,':',clientMessage.decode(FORMAT))
    interface()
    
def send_texts(udpSocket,otherName,portNum):
    global ownClientPort
    while True: #Controls termination of a client to client messaging
            myMessage = input()
            if myMessage == DISCONNECT_PROTOCOL:
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',portNum))
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',ownClientPort))
                break
            if myMessage == '/accept':
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',12001))
                udpSocket.sendto(DISCONNECT_PROTOCOL.encode(FORMAT),('localhost',portNum))
                udpSocket.sendto(DISCONNECT_PROTOCOL.encode(FORMAT),('localhost',ownClientPort))
                break
            else:
                myMessage = myMessage
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',portNum))
    print('You are no longer chatting with',otherName)

def recieve_connection_requests(udpServerSocket):        #Method for being always listening to the udp sokcet for requests only on server
    try:
        while True:
            request_message, address = udpServerSocket.recvfrom(1024)
            if request_message:
                if request_message == DISCONNECT_PROTOCOL:
                    break
                request_message = request_message.decode(FORMAT)    #Request message for user
                print(request_message)  #Message to accept interrupts current interaction
                if ',' in request_message:  #Request information with ports
                    initiate_connection(request_message)
    except Exception:
            pass

def initiate_connection(request_message):
        arrayOfClientInfo = request_message.split(',')
        
        global ownClientPort
        
        #Bind the own client port number with UDP
        my_socket = socket(AF_INET,SOCK_DGRAM) 
        my_socket.bind(("", ownClientPort))
        print('\nYou are now beginning a chat, send /disconnect if you wish to end')        
        print('\nChat with',arrayOfClientInfo[2])
        receivingThread = threading.Thread(target=receive_texts, args=(my_socket,arrayOfClientInfo[0],arrayOfClientInfo[2]),daemon=True)
        sendingThread = threading.Thread(target=send_texts, args=(my_socket,arrayOfClientInfo[2],int(arrayOfClientInfo[3])),daemon=True)
        receivingThread.start()
        sendingThread.start()

def main():
    # TCP socket for initial connection
    global tcp_client_socket
    tcp_client_socket = socket(AF_INET,SOCK_STREAM)
    tcp_client_socket.connect(('localhost', TCPPORT))
    
    #Send client name
    ownClientName = input('Welcome! Thank you for chatting with us.\nEnter your name to begin: ')
    tcp_client_socket.send(ownClientName.encode())
    #Receive the server allocated port
    message = tcp_client_socket.recv(1024).decode()
    global ownClientPort
    ownClientPort = int(message)

    #Bind the request port
    udpForRequestsPort = ownClientPort+100
    
    global udpServerSocket
    udpServerSocket = socket(AF_INET,SOCK_DGRAM) 
    udpServerSocket.bind(('localhost', udpForRequestsPort))
    alwaysAcceptRequests = threading.Thread(target=recieve_connection_requests,args=(udpServerSocket,),daemon=True)
    alwaysAcceptRequests.start()
    interface()
        
def interface():
    print("Here are the messaging options\n\tlist - Gives a list of all available users\n\t/disconnect: terminates communications\nEnter a message to send:")
    engaged = True
    while engaged:     #Controls termination of server socket
        message = input()
        # Send message to server
        if message == DISCONNECT_PROTOCOL:
            engaged = False
        if message == '/accept':
            udpServerSocket.sendto(message.encode(FORMAT),('localhost',12001))
            print('You successfully accepted the chat request')
        if message == 'list':
            tcp_client_socket.send(message.encode(FORMAT))
            #Flow for the client requesting chat:
        else:
            pass
        message = tcp_client_socket.recv(1024).decode(FORMAT)
        print('Online:',message)
        choice = input ('Would you like to start a chat?\n\ty:yes\n\tn:no\n')
        if choice == 'y':
            message=input('Enter the name of the person you would like to chat with:')
            print('Please wait for',message,'to accept your chat request')
            tcp_client_socket.send(message.encode(FORMAT)) 
        if choice == 'n':
            print("Here are the messaging options\n\tlist - Gives a list of all available users\n\t/disconnect: terminates communications\nEnter a message to send:")
        if message == DISCONNECT_PROTOCOL:
            engaged = False

    disconnect(tcp_client_socket,udpServerSocket)

def disconnect(tcp_client_socket,udp_server_socket):
    # Close sockets on client side
    udp_server_socket.sendto(DISCONNECT_PROTOCOL.encode(FORMAT),('localhost',ownClientPort+100))
    udp_server_socket.close()
    
    #Send disconnect message to the server to close server side
    tcp_client_socket.send(DISCONNECT_PROTOCOL.encode(FORMAT))
    
    tcp_client_socket.close()

main()