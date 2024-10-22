import socket
import threading
import queue
from datetime import datetime  # Import untuk timestamp

PORT = 9999
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
PASSWORD = "123"
print(f"Server started at {SERVER}:{PORT}")

messages = queue.Queue()
clients = []
clients_names = []
chat_history_by_users = {}

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER, PORT))

LOG_FILE = "chat_history.txt"

# Fungsi untuk mendapatkan timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Fungsi untuk menyimpan pesan ke file berdasarkan pengguna, dengan timestamp
def save_message(user_pair, message):
    timestamp = get_timestamp()  # Dapatkan timestamp
    full_message = f"[{timestamp}] {message}"
    print(f"Saving message: {full_message}")
    
    if user_pair not in chat_history_by_users:
        chat_history_by_users[user_pair] = []
    chat_history_by_users[user_pair].append(full_message)
    
    with open(LOG_FILE, "a") as file:
        file.write(f"{user_pair}: {full_message}\n")

# Fungsi untuk membaca riwayat pesan dari file berdasarkan pengguna
def load_messages(user_pair):
    try:
        with open(LOG_FILE, "r") as file:
            lines = file.readlines()
            return [line.split(": ", 1)[1] for line in lines if line.startswith(user_pair)]
    except FileNotFoundError:
        return []

# Fungsi membuat kombinasi nama pengguna yang terhubung
def get_user_pair(name1, name2):
    return ":".join(sorted([name1, name2]))

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

                    # Validasi password dan username
                    if password != PASSWORD:
                        server.sendto("Incorrect password.".encode(), addr)
                    elif name in clients_names:
                        server.sendto("Name already taken.".encode(), addr)
                    else:
                        clients_names.append(name)
                        clients.append(addr)
                        server.sendto(f"{name} joined!".encode(), addr)
                        server.sendto("Password accepted. You are now connected.".encode(), addr)

                        # Jika ada dua pengguna di room, kirim riwayat
                        if len(clients_names) == 2:
                            user_pair = get_user_pair(clients_names[0], clients_names[1])
                            chat_history = load_messages(user_pair)
                            if chat_history:
                                for line in chat_history:
                                    server.sendto(line.encode(), addr)

                        broadcast_message = f"{name} has joined the chat!"
                        if len(clients_names) == 2:  # Simpan riwayat jika ada dua pengguna
                            user_pair = get_user_pair(clients_names[0], clients_names[1])
                            save_message(user_pair, broadcast_message)
                        for client in clients:
                            if client != addr:
                                server.sendto(f"[{get_timestamp()}] {broadcast_message}".encode(), client)
                except ValueError:
                    server.sendto("Invalid message format.".encode(), addr)
            else:
                if len(clients_names) == 2:
                    user_pair = get_user_pair(clients_names[0], clients_names[1])
                    save_message(user_pair, decoded_message)
                for client in clients:
                    if client != addr:
                        try:
                            server.sendto(f"[{get_timestamp()}] {decoded_message}".encode(), client)
                        except Exception as e:
                            print(f"Broadcast Error: {e}")
                            clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
