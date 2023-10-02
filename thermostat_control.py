import RPi.GPIO as GPIO
import config
import sqlite3
import socket
import time

# Define host and port
HOST = config.CONTROLLER_IP  # Use your server's IP address or 'localhost' for local testing
PORT = 12345       # Use a port number of your choice

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the host and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

print(f"Listening on {HOST}:{PORT}")


def main():

    current_state = 'initializing'

    setup()
    conn = create_db_connection()

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        data = client_socket.recv(1024).decode('utf-8')

        if data is not None:
            remote_data = parse_message(data)
            print(remote_data)
            update_temp_db(conn, remote_data)
            operational_state, action = determine_state(remote_data[2], current_state)
            run_action(action)
            current_state = operational_state
            client_socket.close()
        else:
            print('no data received')
            time.sleep(60)



def determine_state(temp, current_state):
    if (current_state == 'heat on') & (temp < config.TEMP_TARGET):
        return 'no action'
    elif (current_state == 'heat on') & (temp >= config.TEMP_TARGET):
        return 'heat off'
    elif (current_state == 'heat off') & (temp < config.TEMP_TARGET):
        return 'heat on'
    elif (current_state == 'heat off') & (temp >= config.TEMP_TARGET):
        return 'no action'
    else:
        return 'heat off'


def parse_message(data):
    [timestamp, sensor, value, units, pk] = data.split(',')
    return [timestamp, sensor, float(value), units, pk]


def run_action(action):
    if action == 'heat on':
        heat_on()
    elif action == 'heat off':
        heat_off()
    elif action == 'no action':
        pass


def heat_on():
    GPIO.output(config.RELAY_PIN, True)


def heat_off():
    GPIO.output(config.RELAY_PIN, False)


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(config.RELAY_PIN, GPIO.OUT)
    heat_off()


def create_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(config.DB_PATH)
    except:
        print('error connecting to db')
    return conn


def update_temp_db(conn, temp):
    sql = ''' INSERT INTO temps(timestamp,sensor,value,units,pk)
              VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, temp)
    conn.commit()
    return cur.lastrowid


if __name__ == "__main__":
    main()
