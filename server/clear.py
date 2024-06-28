import paho.mqtt.client as mqtt
import sqlite3
import socket
from datetime import datetime

# MQTT broker details
mqttBroker_address = "iotsmarthouse.go.ro"
mqttPort = 1883
mqttUser = "baiaMare"
mqttPassword = "Ares"

# Socket server details
socketServer_address = '192.168.100.85'
socketServer_port = 12345

# Function to save message to database
def save_to_database(topic, message):
    try:
        # Create a database for each topic
        db_name = f"{topic.replace('/', '_')}_data.db"
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, message TEXT, timestamp TIME)")
        cursor.execute("INSERT INTO messages (topic, message, timestamp) VALUES (?, ?, ?)", (topic, message, datetime.now().strftime("%H:%M:%S")))
        conn.commit()
        print(f"Message saved to database '{db_name}' for topic '{topic}'")
    except sqlite3.Error as e:
        print("Error saving message to database:", e)
    finally:
        conn.close()

# Function to send the database file through socket
def send_database_file(file_path, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    s.sendall(chunk)
        print(f"Database file '{file_path}' sent successfully to {host}:{port}.")
    except Exception as e:
        print("Error sending database file:", e)

# Callback function when a message is received
def on_message(client, userdata, message):
    received_message = message.payload.decode()
    mqttTopic = message.topic
    print(f"Received message on topic '{mqttTopic}': {received_message}")

    # Check if the received message is on the "clear" topic

    if mqttTopic == "send":
        # Send the database file through socket for both "masa" and "temp" topics
        send_database_file('masa_data.db', socketServer_address, socketServer_port)
        send_database_file('temp_data.db', socketServer_address, socketServer_port)
    else:
        # Save message to the respective database based on the topic
        save_to_database(mqttTopic, received_message)

# Create an MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Set the username and password
client.username_pw_set(username=mqttUser, password=mqttPassword)

# Assign the on_message callback function
def on_message(client, userdata, message):
    received_message = message.payload.decode()
    mqttTopic = message.topic
    print(f"Received message on topic '{mqttTopic}': {received_message}")

    # Check if the received message is on the "clear" topic
    if(mqttTopic != "clear"):
        # Save message to the respective database based on the topic
        save_to_database(mqttTopic, received_message)

        # Check if the received message is on the "send" topic
        if mqttTopic == "send":
            # Send the database file through socket for both "masa" and "temp" topics
            send_database_file('masa_data.db', socketServer_address, socketServer_port)
            send_database_file('temp_data.db', socketServer_address, socketServer_port)

# Create an MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Set the username and password
client.username_pw_set(username=mqttUser, password=mqttPassword)

# Assign the on_message callback function
client.on_message = on_message

# Connect to the broker
client.connect(mqttBroker_address, mqttPort)

# Subscribe to the weight, temperature, "clear", and "send" topics
client.subscribe("/Cantar/Robert/Masa")
client.subscribe("/Cantar/Robert/Temp")
client.subscribe("clear")
client.subscribe("send")

# Start the MQTT client's loop to handle incomiang messages
client.loop_forever()
