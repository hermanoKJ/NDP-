import socket
import os

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5001))

file_to_send = "school pic.jpeg" 

client_socket.send(f"{file_to_send}<NAME_END>".encode())

with open(file_to_send, 'rb') as file:
    print(f"Sending {file_to_send}...")
    data = file.read(1024)
    while data:
        client_socket.send(data)
        data = file.read(1024)

print("File sent completely!")
client_socket.close()