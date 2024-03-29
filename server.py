import socket
import threading

DISCONNECT_PROTOCOL = "/disconnect"
CONNECTIONPORT = 12000
CLIENTPORT = 13000
lock = threading.Lock()
usernames=[]
available=[]
userports=[]

def increment_port():
    global CLIENTPORT
    with lock:
        CLIENTPORT += 1

def handle_client(connectionSocket,addr):
    print(f"[NEW CONNECTION] {addr} connected")
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")
    connected = True
    
    clientName = connectionSocket.recv(1024).decode()
    increment_port()
    portString = str(CLIENTPORT)
    portNumber = CLIENTPORT
    connectionSocket.send((portString) .encode())
    print(clientName, 'is now available on',portNumber)       #Write the port to the array
    
    usernames.append(clientName)
    available.append(clientName)
    userports.append(CLIENTPORT)
    
    while connected:
        # Receive message from client
        message = connectionSocket.recv(1024).decode()
        if message:
            print("Received message from client:", message)
            if message == DISCONNECT_PROTOCOL:
                connected = False
            elif 'ADD' in message:
                while True:
                    new_status=message.split(',')
                    available.append(new_status[1])
                    print('[AVAILABLE]',new_status[1],'is free to chat!')
                    break
            elif message == 'list':
                while True:
                    availableClients = ','.join(str(x) for x in available)
                    #Send a list the available clients
                    connectionSocket.send(availableClients.encode())
                    choice = connectionSocket.recv(1024).decode()
                    if (choice == 'CONNECT'):
                        wantedClientName = connectionSocket.recv(1024).decode()
                        for i in range (len(usernames)):
                            if usernames[i] == wantedClientName:
                                connection_request(i,portNumber,clientName) 
                    else:
                        break
            else:
                connectionSocket.send('Please send a valid function'.encode())
    print(clientName,'has disconnected')
    usernames.remove(clientName)
    for user in available:
        if user == clientName:
            available.remove(clientName)    
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-2}")
    connectionSocket.close()

def connection_request(i,client1Port,client1Name):  #i has client 2 info
        udpForRequestsPort = userports[i]+100
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_socket.bind(('localhost',12001))  #New port for connection requests
        message='[SERVER NOTICE] ' + client1Name + " wants to chat! Type /accept to go to their chat.\n"
        udp_server_socket.sendto(message.encode(),('localhost',udpForRequestsPort))
        
        while True:
            request_message, address = udp_server_socket.recvfrom(1024)   
            if request_message:
                if(request_message.decode('utf-8') == '/accept'):
                    #Remove engaged clients from the available array
                    available.remove(client1Name)
                    available.remove(usernames[i])
                    print('[BUSY]',client1Name,'and',usernames[i],'are chatting')
                    #Send connection string
                    request_message = str(client1Name) + "," + str(client1Port) + "," + str(usernames[i]) + "," + str(userports[i])
                    request_message_other = str(usernames[i]) + "," + str(userports[i])  + "," +str(client1Name) + "," + str(client1Port)
                    udp_server_socket.sendto(request_message_other.encode(),('localhost',udpForRequestsPort))
                    udp_server_socket.sendto(request_message.encode(),('localhost',client1Port+100))
                    break
                else:
                    request_message = ''    #Some kind of protocol that resets the interaction because the request was rejected

def startServer():
    # TCP socket for initial connection
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(('localhost', CONNECTIONPORT))
    tcp_server_socket.listen(1)
    print(f"[LISTENING] Server is listening with TCP on {CONNECTIONPORT}")
    while True:
        # Accept TCP connection    
        tcp_client_socket, addr = tcp_server_socket.accept()
        new_client = threading.Thread(target=handle_client, args=(tcp_client_socket,addr))
        new_client.start()
        
startServer()
