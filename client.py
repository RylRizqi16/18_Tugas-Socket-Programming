import socket
import threading
import random

SERVER_IP = input("Enter IP Address: ")
PORT = int(input("Enter port number: "))  # Convert port to integer
ADDRESS = (SERVER_IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.bind(('', random.randint(8000, 9000)))

name = input("Nickname: ")
password = input("Enter the password: ")

# Flag to check if the client is authenticated
authenticated = False

def receive():
    global authenticated
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decoded_message = message.decode()
            print(decoded_message)

            # Check for authentication message
            if decoded_message == "Password accepted. You are now connected.":
                authenticated = True
            elif decoded_message == "Incorrect password.":
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

client.sendto(f"password:{password}".encode(), ADDRESS)

# Wait for authentication
while not authenticated:
    pass  # Do nothing until authenticated or server responds

# Once authenticated, proceed with signup
client.sendto(f"SIGNUP_TAG:{name}".encode(), ADDRESS)

while True:
    message = input()
    if message == "!q":
        print("Exiting...")
        break  # Exit the loop, stopping the client
    else:
        client.sendto(f"{name} : {message}".encode(), ADDRESS)

# Close the client socket
client.close()
