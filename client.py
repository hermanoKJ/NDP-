import socket
import os

# Configuration variables make it easier to update later
HOST = 'localhost'
PORT = 5001
FILE_TO_SEND = "school pic.jpeg"
BUFFER_SIZE = 4096

#1. Initialize and connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5001))

file_to_send = "school pic.jpeg" 

#2. Send filename with delimiter (using sendall)
client_socket.sendall(f"{file_to_send}<NAME_END>".encode('utf-8'))

#Read and send file data
with open(file_to_send, 'rb') as file:
    print(f"Sending {file_to_send}...")
    data = file.read(BUFFER_SIZE)
    while data:
        client_socket.send(data)
        data = file.read(BUFFER_SIZE)

print("File sent completely!")
client_socket.close()