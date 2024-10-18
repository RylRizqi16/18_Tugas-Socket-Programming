import socket
import threading
import queue

PORT = 9999
SERVER = socket.gethostbyname(socket.gethostname())  
ADDRESS = (SERVER, PORT)
PASSWORD = "123" 
print(SERVER)

messages = queue.Queue()

clients = []
clients_names = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER, PORT))

def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except Exception as e:
            print(f"Receive Error: {e}")
            pass

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded_message = message.decode()
            print(f"Received from {addr}: {decoded_message}")

            if addr not in clients:
                try:
                    name, password = decoded_message.split(":")
                    name = name.strip()
                    password = password.strip()

                    if password == PASSWORD and name not in clients_names:
                        clients_names.append(name)
                        clients.append(addr) 
                        server.sendto(f"{name} joined!".encode(), addr)
                        server.sendto("Password accepted. You are now connected.".encode(), addr)

                        broadcast_message = f"{name} has joined the chat!"
                        for client in clients:
                            if client != addr:
                                server.sendto(broadcast_message.encode(), client)
                    elif password != PASSWORD:
                        server.sendto("Incorrect password.".encode(), addr)
                    elif name in clients_names:
                        server.sendto("Name already taken.".encode(), addr)
                except ValueError:
                    server.sendto("Invalid message format.".encode(), addr)
            else:
                for client in clients:
                    if client != addr:
                        try:
                            server.sendto(message, client)
                        except Exception as e:
                            print(f"Broadcast Error: {e}")
                            clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
