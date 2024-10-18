import socket
import threading
import random

SERVER_IP = input("Enter IP Address: ")
PORT = int(input("Enter port number: ")) 
ADDRESS = (SERVER_IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.bind(('', random.randint(8000, 9000)))

name = input("Nickname: ")
password = input("Enter the password: ")

def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            print(decoded_message)

            # Check for authentication message
            if decoded_message == "Incorrect password.":
                print("Exiting...")
                client.close()
                break
            elif decoded_message == "Name already taken.":
                print("Exiting...")
                client.close()
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Start a thread to listen for incoming messages
t = threading.Thread(target=receive)
t.daemon = True  # Ensures thread exits when the main program exits
t.start()

# Once authenticated, proceed with signup
client.sendto(f"{name}:{password}".encode(), ADDRESS)

while True:
    message = input()
    if message == "!q":
        print("Exiting...")
        break  # Exit the loop, stopping the client
    else:
        client.sendto(f"{name} : {message}".encode(), ADDRESS)

# Close the client socket
client.close()