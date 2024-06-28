import paho.mqtt.client as mqtt
import random

# MQTT Broker details
mqttBroker_address = "iotsmarthouse.go.ro"
mqttPort = 1883
mqttUser = "baiaMare"
mqttPassword = "Ares"

# Number of random values to publish
num_values = 30

# Generate random values
random_values = [random.randint(50, 500) for _ in range(num_values)]

# Create a string with all values separated by space
values_string = " ".join(map(str, random_values))

# Publish the string
def publish_values():
    client = mqtt.Client()
    client.username_pw_set(username=mqttUser, password=mqttPassword)
    client.connect(mqttBroker_address, mqttPort)

    client.publish("/Cantar/Robert/Frecventa", values_string)
    print("Published:", values_string)

    client.disconnect()
    print("Publishing completed.")

# Execute the function
publish_values()
