import RPi.GPIO as GPIO
import config
import sqlite3
import socket

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

current_state = 'initializing'
def main():
    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        data = client_socket.recv(1024).decode('utf-8')

        if data != None:
            remote_data = parse_message(data)
            operational_state, action = determine_state(remote_data, current_state)
            run_action(action)
            current_state = operational_state
            client_socket.close()

def determine_state(remote_data, current_state):
    if (current_state == 'heat on') & (remote_data.temp < config.TEMP_TARGET):
        return 'no action'
    elif (current_state == 'heat on') & (remote_data.temp >= config.TEMP_TARGET):
        return 'heat off'
    elif (current_state == 'heat off') & (remote_data.temp < config.TEMP_TARGET):
        return 'heat on'
    elif (current_state == 'heat off') & (remote_data.temp >= config.TEMP_TARGET):
        return 'no action'
    else:
        return 'heat off'

def parse_message(data):
    return {}

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

def create_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(config.DB_PATH)
    except Error as e:
        print(e)
    return conn

def update_temp_db(conn, temp):
    sql = ''' INSERT INTO temps(timestamp,sensor,value,units,pk)
              VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, temp)
    conn.commit()
    return cur.lastrowid