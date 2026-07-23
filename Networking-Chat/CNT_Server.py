import socket

# Create a socket
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define host
Host = "0.0.0.0"

# Define port
Port = 5000

# Bind socket to address
ServerSocket.bind((Host, Port))

# Start listening
ServerSocket.listen(5)

# Print server status
print("Server is running...")
print("Waiting for connection...")

# Accept one client
ClientSocket, ClientAddress = ServerSocket.accept()

# Show client address
print("Client connected from:", ClientAddress)

# Start chat loop
while True:
    # Receive message from client
    ClientMessage = ClientSocket.recv(1024).decode()

    # If client disconnects, stop
    if not ClientMessage:
        break

    # Print client message
    print("Client says:", ClientMessage)

    # Ask server user for reply
    ServerReply = input("Enter reply: ")

    # Send reply to client
    ClientSocket.send(ServerReply.encode())

    # Optional exit
    if ClientMessage.lower() == "quit":
        break

# Close connection
ClientSocket.close()
ServerSocket.close()
