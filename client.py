from socket import *
import threading
DISCONNECT_PROTOCOL = "/disconnect"
FORMAT = 'utf-8'
TCPPORT = 12000
ownClientPort = 13000     #for now
ownClientName = ''
serverIP = gethostbyname(gethostname())

def receive_texts(udpSocket,myName,otherName):
    while True: #Controls termination of a client to client messaging
        clientMessage, address = udpSocket.recvfrom(1024)
        print(myName,':',clientMessage.decode(FORMAT))
        if clientMessage == DISCONNECT_PROTOCOL:
            print(otherName, 'is no longer in the chat. You might want to disconnect')
            
    
def send_texts(udpSocket,otherName,portNum):
    while True: #Controls termination of a client to client messaging
            myMessage = input()
            if myMessage == DISCONNECT_PROTOCOL:
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',portNum))
                break
            if myMessage == '/accept':
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',12001))
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
        receivingThread = threading.Thread(target=receive_texts, args=(my_socket,arrayOfClientInfo[2],arrayOfClientInfo[2]),daemon=True)
        sendingThread = threading.Thread(target=send_texts, args=(my_socket,arrayOfClientInfo[2],int(arrayOfClientInfo[3])),daemon=True)
        receivingThread.start()
        sendingThread.start()
        while sendingThread.is_alive(): #Have something here to keep the connection here or some method something
            pass
        my_socket.close()

def main():
    # TCP socket for initial connection
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
    udpServerSocket = socket(AF_INET,SOCK_DGRAM) 
    udpServerSocket.bind(('localhost', udpForRequestsPort))
    alwaysAcceptRequests = threading.Thread(target=recieve_connection_requests,args=(udpServerSocket,),daemon=True)
    alwaysAcceptRequests.start()
    
    print("Here are the messaging options\n\tlist - Gives a list of all available users\n\t/disconnect: terminates communications\nEnter a message to send:")
    while True:     #Controls termination of server socket
        message = input()
        # Send message to server
        if message == DISCONNECT_PROTOCOL:
            break
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
            tcp_client_socket.send(message.encode(FORMAT))
            print('Please wait for',message,'to accept your chat request')

    disconnect(tcp_client_socket,udpServerSocket)
        

def disconnect(tcp_client_socket,udp_server_socket):
    #Send disconnect message to the server to close server side
    tcp_client_socket.send(DISCONNECT_PROTOCOL.encode(FORMAT))
    
    # Close sockets on client side
    udp_server_socket.close()
    tcp_client_socket.close()

main()