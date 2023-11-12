import socket
import time
import RPi.GPIO as GPIO
import config
import sqlite3
import datetime

# Define host and port
HOST = config.CONTROLLER_IP  # Use your server's IP address or 'localhost' for local testing
PORT = 12345       # Use a port number of your choice

last_message_timestamp = -9999.99999




def determine_state(temp, current_state):
    if (current_state == 'heat on') & (temp < config.TEMP_TARGET):
        print('temp below target, heat remaining on')
        return ['heat on','no action']
    elif (current_state == 'heat on') & (temp >= config.TEMP_TARGET):
        print('temp above target, heat turning off')
        return ['heat off', 'heat off']
    elif (current_state == 'heat off') & (temp < config.TEMP_TARGET):
        print('temp below target, heat turning on')
        return ['heat on', 'heat on']
    elif (current_state == 'heat off') & (temp >= config.TEMP_TARGET):
        print('temp above target, heat remaining off')
        return ['heat off','no action']
    elif current_state == 'initializing':
        print('initialized')
        return ['heat off', 'heat off']
    else:
        return ['unknown state', 'heat off']


def parse_message(data):
    split_data = data.split(',')
    if len(split_data) == 5:
        split_data[2] = float(split_data[2])
        return split_data
    else:
        return [None, None, None, None, None]


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


def update_event_db(conn,event):
    sql = ''' INSERT INTO events(timestamp,event,pk)
                  VALUES(?,?,?)'''
    cur = conn.cursor()
    ts = timestamp()
    cur.execute(sql, [ts, event, ts + '-' + event])
    conn.commit()
    return cur.lastrowid


def timestamp():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def formatted_time_to_timestamp(t):
    element = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
    timestamp = datetime.datetime.timestamp(element)
    return timestamp


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    while True:
        print("Waiting for connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(1024).decode('utf-8')

        if data is not None:
            remote_data = parse_message(data)
            print(remote_data)
            if remote_data[0] is not None:
                last_message_timestamp = formatted_time_to_timestamp(remote_data[0])
                update_temp_db(conn, remote_data)
                operational_state, action = determine_state(remote_data[2], current_state)
                run_action(action)
                current_state = operational_state
        else:
            print('no data received')
            time.sleep(30)

        # Exchange information here
        data = "data received!"
        client_socket.sendall(data.encode())

        # Close the connection
        client_socket.close()
        time.sleep(60)  # Sleep for X minutes


if __name__ == "__main__":
    current_state = 'initializing'
    conn = create_db_connection()
    setup()
    server()




