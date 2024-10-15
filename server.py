import socket
import threading
import queue

PORT = 9999
SERVER = socket.gethostbyname(socket.gethostname())  
ADDRESS = (SERVER, PORT)
PASSWORD = "123" 
print(SERVER)

# Queue to store incoming messages
messages = queue.Queue()

# List to track connected clients
clients = []

# Create UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER, PORT))

# Function to receive messages
def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)  # Receive message and client address
            messages.put((message, addr))  # Add message to the queue
        except Exception as e:
            print(f"Receive Error: {e}")
            pass

# Function to broadcast messages to all clients
def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()  # Get message from queue
            decoded_message = message.decode()
            print(f"Received from {addr}: {decoded_message}")

            if addr not in clients:
                # Check if the message contains the password
                if decoded_message.startswith("password:"):
                    password = decoded_message.split(":")[1].strip()
                    if password == PASSWORD:
                        clients.append(addr)  # Add client to authenticated clients list
                        server.sendto("Password accepted. You are now connected.".encode(), addr)
                    else:
                        server.sendto("Incorrect password.".encode(), addr)
            else:
                # If the client is already authenticated, check for signup tag
                if decoded_message.startswith("SIGNUP_TAG"):
                    name = decoded_message.split(":")[1].strip()
                    # Notify all clients that the user has joined
                    for client in clients:
                        server.sendto(f"{name} joined!".encode(), client)
                else:
                    # Forward the message to all connected clients
                    for client in clients:
                        try:
                            if client != addr:
                                server.sendto(message, client)
                        except Exception as e:
                            print(f"Broadcast Error: {e}")
                            clients.remove(client)  # Remove client if there's an error sending

# Create and start threads for receiving and broadcasting messages
t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
