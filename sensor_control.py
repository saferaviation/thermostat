import socket
import datetime
import time
import config


# Define the remote server's host and port
HOST = '192.168.86.45'  # Replace with the remote server's IP address or hostname
PORT = 12345          # Replace with the remote server's port number

ROOM = 'JULIAN'

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def get_temperature():
    return 75.0


def timestamp():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def main():
    # Connect to the remote server
    while True:
        try:
            client_socket.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}")
        except ConnectionRefusedError:
            print(f"Connection to {HOST}:{PORT} was refused. Ensure the server is running.")
            exit(1)

        # Send data to the server
        temp = get_temperature()
        ts = timestamp()
        pk = ts + ',' + ROOM + ',' + str(temp)
        message = ts + ',' + ROOM + ',' + str(temp) + ',F,' + pk

        client_socket.sendall(message.encode('utf-8'))

        # Receive data from the server
        data = client_socket.recv(1024)
        print(f"Received from server: {data.decode('utf-8')}")

        # Close the socket
        client_socket.close()
        time.sleep(60)

if __name__ == "__main__":
    main()
