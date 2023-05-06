import socket
import pickle  # used to send over the list of users
import threading

# Allow connections from outside of the server
HOST = '' # Obtains the IP of the server
PORT = 9898

# Create empty set so that it can maintain a list of the connected clients
clients = set()
clients_lock = threading.Lock()

# Keep track of connected users
users = []

# Handling new client connections
def add_client(client, addr):
    # Get Clients username and show that they have been connected
    username = client.recv(1024).decode("utf-8")
    users.append(username)

    print(
        f"*** {username} Connected (IP: (IP: {addr[0]} | Remote addr: {addr[1]}) ***")

    try:
        active_connection = True

        while active_connection:
            # Recever the message that was sent from the client
            msg = client.recv(1024).decode("utf-8")

            if not msg:
                break

            # Condition to Exit the chatting program (Disconnect from server)
            if msg == "!Exit":
                active_connection = False
                users.remove(username)
                list_active_users = pickle.dumps(users)
                print(f"*** <{username}> (IP: {addr[0]} | Remote addr: {addr[1]}) Disconnected ***")

            # Get all of the active users that are currently connected to the server
            elif msg == "!GetAllActiveUsers":
                # sends the user list over tcp
                list_active_users = pickle.dumps(users)

            # Display in gui and show everyone that the user has connected to server
            elif msg == "!ShowUserHasConnected":
                message = (f"*** {username} Connected ***".encode("utf-8"))

            else:
                message = (f"<{username}> {msg}".encode("utf-8"))

            # Loop through all connected clients and send the message to each one
            with clients_lock:
                for c in clients:
                    try:
                        if msg == "!GetAllActiveUsers" or msg == "!Exit":
                            c.sendall(list_active_users)
                        else:
                            c.sendall(message)
                    except:
                        # Remove messages from the clients set, if there is an error sending
                        clients.remove(c)
    except:
        # Show that there is an error with the client
        print(f"Error with client (IP: {addr[0]} | Remote addr: {addr[1]})")
    finally:
        # Remove the client from the clients set and close the socket
        with clients_lock:
            clients.remove(client)
        client.close()


'''
**********************************************************************
*********************************MAIN*********************************
**********************************************************************
'''

if __name__ == "__main__":
    # Create Socket object for server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind Local IP (Server IP) of the socket to the port
    server.bind((HOST, PORT))

    print("Allowing Connections...")

    # Ready to accept requests
    server.listen()

    while True:
        try:
            # When a new client connects, accept the connection and create a new thread to handle it
            client, addr = server.accept()
            thread = threading.Thread(target=add_client, args=(client, addr))
            thread.start()

            # Add new clients to the set
            with clients_lock:
                clients.add(client)
        except KeyboardInterrupt:
            print("Close Connections...")
            client.close()
            raise SystemExit
        except:
            print("Error accepting new client connection")
            break
