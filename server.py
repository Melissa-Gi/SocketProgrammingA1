import socket
import threading

DISCONNECT_PROTOCOL = "!DISCONNECT"
CONNECTIONPORT = 12000
CLIENTPORT = 13000

def capitalize_message(message):
    return message.upper()

def handle_client(connectionSocket,addr):
    print(f"[NEW CONNECTION] {addr} connected")
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")
    connected = True
    while connected:
        # Receive message from client
        message = connectionSocket.recv(1024).decode()
        if message:
            print("Received message from client:", message)
            if message == DISCONNECT_PROTOCOL:
                connected = False
        # Capitalize the message
        capitalized_message = capitalize_message(message)

        # UDP socket for sending the capitalized message
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_socket.sendto(capitalized_message.encode(), ('localhost', 13000))
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-2}")
    connectionSocket.close()
    udp_server_socket.close()

def startServer():
    # TCP socket for initial connection
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(('localhost', CONNECTIONPORT))
    tcp_server_socket.listen(1)
    print(f"[LISTENING] Server is listening with TCP on {CONNECTIONPORT}")
    while True:
    # Accept TCP connection
        tcp_client_socket, addr = tcp_server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(tcp_client_socket,addr))
        thread.start()
        # -1 to exclude server thread
        
startServer()
