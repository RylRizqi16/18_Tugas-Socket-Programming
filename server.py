import socket
import threading
import queue
import binascii  # Import binascii untuk CRC32
from datetime import datetime
from rsa_module import generate_keys, encrypt, decrypt

PORT = 9999
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
PASSWORD = "123"
print(f"Server started at {SERVER}:{PORT}")

messages = queue.Queue()
clients = []
clients_names = []

# Generate RSA keys
public_key, private_key, n = generate_keys()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER, PORT))

LOG_FILE = "chat_history.txt"

# Fungsi untuk mendapatkan timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Fungsi untuk menyimpan pesan ke file dengan timestamp
def save_message(message):
    timestamp = get_timestamp()  
    full_message = f"[{timestamp}] {message}"
    print(f"Saving message: {full_message}")
    
    with open(LOG_FILE, "a") as file:
        file.write(f"{full_message}\n")

# Fungsi untuk memuat seluruh pesan dari file riwayat obrolan
def load_messages():
    try:
        with open(LOG_FILE, "r") as file:
            lines = file.readlines()
            return [line.strip() for line in lines]
    except FileNotFoundError:
        return []

def receive():
    while True:
        message, addr = server.recvfrom(1024)
        if message == b'GET_PUBLIC_KEY':
            # Send the public key to the client
            server.sendto(f"{public_key},{n}".encode(), addr)
            continue

        decrypted_message = decrypt(eval(message.decode()), private_key, n)
        messages.put((decrypted_message.encode(), addr))

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

                    # Validate password and username
                    if password != PASSWORD:
                        server.sendto("Incorrect password.".encode(), addr)
                    elif name in clients_names:
                        server.sendto("Name already taken.".encode(), addr)
                    else:
                        clients_names.append(name)
                        clients.append(addr)
                        server.sendto(f"{name} joined!".encode(), addr)
                        server.sendto("Password accepted. You are now connected.".encode(), addr)

                        # Send chat history to new user
                        chat_history = load_messages()
                        if chat_history:
                            for line in chat_history:
                                server.sendto(line.encode(), addr)

                        # Notify all users about the new user
                        broadcast_message = f"{name} has joined the chat!"
                        save_message(broadcast_message)
                        for client in clients:
                            if client != addr:
                                server.sendto(f"[{get_timestamp()}] {broadcast_message}".encode(), client)
                except ValueError:
                    server.sendto("Invalid message format.".encode(), addr)
            else:
                # Verif checksum
                try:
                    name, message_text, received_checksum = decoded_message.rsplit(":", 2)
                    received_checksum = int(received_checksum)
                    calculated_checksum = binascii.crc32(message_text.encode())

                    if received_checksum == calculated_checksum:
                        # Save and broadcast message if checksum is correct
                        broadcast_message = f"{name}: {message_text}"
                        save_message(broadcast_message)
                        for client in clients:
                            if client != addr:
                                server.sendto(f"[{get_timestamp()}] {broadcast_message}".encode(), client)
                    else:
                        # NNgabarin kalau pesan rusak
                        server.sendto("Message integrity compromised!".encode(), addr)

                except ValueError:
                    server.sendto("Invalid message format.".encode(), addr)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
