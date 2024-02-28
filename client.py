from socket import *
import threading
DISCONNECT_PROTOCOL = "/disconnect"
FORMAT = 'utf-8'
TCPPORT = 12000
ownClientPort = 13000     #for now
ownClientName = ''
serverIP = gethostbyname(gethostname())

def receive_texts(udpSocket,otherName):
    while True: #Controls termination of a client to client messaging
        clientMessage, address = udpSocket.recvfrom(1024)
        print(clientMessage.decode(FORMAT))
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
                udpSocket.sendto(myMessage.encode(FORMAT),('localhost',portNum))
    print('You are no longer chatting with',otherName)

def recieve_connection_requests(udpServerSocket):        #Method for being always listening to the udp sokcet for requests only on server
    while True:
        request_message, address = udpServerSocket.recvfrom(1024)
        if request_message:
            request_message = request_message.decode(FORMAT)    #Request message for user
            print(request_message)  #Message to accept interrupts current interaction
            if ',' in request_message:  #Request information with ports
                initiate_connection(request_message)


def initiate_connection(request_message):
        arrayOfClientInfo = request_message.split(',')
        
        global ownClientPort
        
        #Bind the own client port number with UDP
        my_socket = socket(AF_INET,SOCK_DGRAM) 
        my_socket.bind(("", ownClientPort))
        print('You are now beginning a chat, send /disconnect if you wish to end')        
        print('Chat with',arrayOfClientInfo[2])
        receivingThread = threading.Thread(target=receive_texts, args=(my_socket,arrayOfClientInfo[2]))
        sendingThread = threading.Thread(target=send_texts, args=(my_socket,arrayOfClientInfo[2],int(arrayOfClientInfo[3])))
        receivingThread.start()
        sendingThread.start()
        while sendingThread.is_alive(): #Have something here to keep the connection here or some method something
            pass

def main():
    # TCP socket for initial connection
    tcp_client_socket = socket(AF_INET,SOCK_STREAM)
    tcp_client_socket.connect(('localhost', TCPPORT))
    
    #Send client name
    ownClientName = input('Enter your name: ')
    tcp_client_socket.send(ownClientName.encode())
    #Receive the server allocated port
    message = tcp_client_socket.recv(1024).decode()
    global ownClientPort
    ownClientPort = int(message)

    #Bind the request port
    udpForRequestsPort = ownClientPort+100
    udpServerSocket = socket(AF_INET,SOCK_DGRAM) 
    udpServerSocket.bind(('localhost', udpForRequestsPort))
    alwaysAcceptRequests = threading.Thread(target=recieve_connection_requests,args=(udpServerSocket,))
    alwaysAcceptRequests.start()
    
    print("Enter a message to send. Use /disconnect to terminate: ")
    while True:     #Controls termination of server socket
        message = input()
        # Send message to server
        if message == DISCONNECT_PROTOCOL:
            break
        if message == '/accept':
            udpServerSocket.sendto(message.encode(),('localhost',12001))
            print('You successfully accepted the chat request')
        if message == 'list':
            tcp_client_socket.send(message.encode())
        else:
            pass

        #Flow for the client requesting chat:
        message = tcp_client_socket.recv(1024)
        print(message)
        message=input('Who do you want to chat to? : /n')
        tcp_client_socket.send(message.encode())
        print('Please wait for',message,'to accept your chat request')
        

def disconnect(tcp_client_socket,udp_client_socket,udp_server_socket):
    #Send disconnect message to the server to close server side
    tcp_client_socket.send(DISCONNECT_PROTOCOL.encode())
    
    # Close sockets on client side
    udp_client_socket.close()
    udp_server_socket.close()
    tcp_client_socket.close()

main()
