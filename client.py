import socket
import threading
import random
import binascii  # Import binascii untuk CRC32
from rsa_module import encrypt

SERVER_IP = input("Enter IP Address: ")
PORT = int(input("Enter port number: ")) 
ADDRESS = (SERVER_IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('', random.randint(8000, 9000)))

# Request the public key from the server
client.sendto(b'GET_PUBLIC_KEY', ADDRESS)
public_key_data, _ = client.recvfrom(1024)
public_key, n = map(int, public_key_data.decode().split(','))

name = input("Nickname: ")
password = input("Enter the password: ")

# Encrypt and send authentication message
auth_message = f"{name}:{password}"
encrypted_auth_message = encrypt(auth_message, public_key, n)
client.sendto(','.join(map(str, encrypted_auth_message)).encode(), ADDRESS)

stop_receiving = False

def receive():
    while not stop_receiving:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            print(decoded_message)
            if decoded_message in ["Incorrect password.", "Name already taken."]:
                print("Exiting...")
                client.close()
                break
        except Exception as e:
            if not stop_receiving:
                print(f"Error receiving message: {e}")
            break

t = threading.Thread(target=receive)
t.daemon = True
t.start()

while True:
    message = input()
    if message == "!q":
        print("Exiting...")
        stop_receiving = True
        break
    else:
        # Calculate checksum using CRC32
        checksum = binascii.crc32(message.encode())
        message_with_checksum = f"{name}:{message}:{checksum}"
        
        # Encrypt the message with checksum
        encrypted_message = encrypt(message_with_checksum, public_key, n)
        client.sendto(','.join(map(str, encrypted_message)).encode(), ADDRESS)

client.close()
t.join()
