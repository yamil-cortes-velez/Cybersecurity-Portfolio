import socket

# Create client socket
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Ask user for server IP
ServerIP = input("Enter server IP: ")

# Ask user for server port
ServerPort = int(input("Enter server port: "))

# Connect to server
ClientSocket.connect((ServerIP, ServerPort))

# Confirm connection
print("Connected to server successfully.")

# Start chat loop
while True:
    # Ask user for message
    ClientMessage = input("Enter a message: ")

    # Send message to server
    ClientSocket.send(ClientMessage.encode())

    # If user wants to quit, stop
    if ClientMessage.lower() == "quit":
        break

    # Receive reply from server
    ServerReply = ClientSocket.recv(1024).decode()

    # Print reply
    print("Server says:", ServerReply)

# Close socket
ClientSocket.close()
