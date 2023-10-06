import socket
import datetime
import time
import config
import glob


# Define the remote server's host and port
HOST = '192.168.86.45'  # Replace with the remote server's IP address or hostname
PORT = 12345          # Replace with the remote server's port number

ROOM = 'JULIAN'

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f


def get_temperature():
    return read_temp()[1]


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
