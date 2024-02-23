# Get Message From mqtt and send mqtt message after receiving
# How to use: python3 mqttReceiver.py [mqttBrokerIP] [mqttBrokerPort] [mqttBrokerTopic]
# Example: python3 mqttReceiver.py

import threading
import paho.mqtt.client as mqtt
import json
import os
import keyboard
import time

DEVICE_NAME = "tablet/vstup"
mqttBrokerTopic = "building/karlstejn/device/status"
mqttBrokerIP = "192.168.1.100"
mqttBrokerPort = 1883
topicSubscribe = DEVICE_NAME + "/#"

mqttClient = None

def shutdown_computer():
    if os.name == 'nt':
        os.system('shutdown /s /t 0')
    elif os.name == 'posix':
        os.system('sudo shutdown now')
    else:
        print('Unsupported operating system.')

def reboot_computer():
    if os.name == 'nt':
        os.system('shutdown /r /t 0')
    elif os.name == 'posix':
        os.system('sudo reboot')
    else:
        print('Unsupported operating system.')

def mqtt_client_thread():
    global mqttClient

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        payload = {
            "topic": DEVICE_NAME,
            "message": "Device with topic " + DEVICE_NAME + " connected to broker",
            "type": "info",
        }
        payload = json.dumps(payload)
        mqttClient.publish(mqttBrokerTopic, payload)

    def on_message(client, userdata, msg):
        # Check if topic ends in /shutdown
        if msg.topic.endswith("/shutdown"):
            print("Shutting down")
            payload = {
                "topic": DEVICE_NAME,
                "message": "Device with topic " + DEVICE_NAME + " shut down by user",
                "type": "shutdown"
            }
            payload = json.dumps(payload)
            mqttClient.publish(mqttBrokerTopic, payload)
            shutdown_computer()
        elif msg.topic.endswith("/reboot"):
            print("Rebooting")
            payload = {
                "topic": DEVICE_NAME,
                "message": "Device with topic " + DEVICE_NAME + " rebooted by user",
                "type": "reboot"
            }
            payload = json.dumps(payload)
            mqttClient.publish(mqttBrokerTopic, payload)
            reboot_computer()     

    mqttClient = mqtt.Client()
    mqttClient.connect(mqttBrokerIP, mqttBrokerPort, 60)
    mqttClient.subscribe(topicSubscribe, 0)

    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message

    mqttClient.loop_start()

def keypress_thread():
    global mqttClient

    while True:
        # Example: Press 'p' to publish a message
        if keyboard.is_pressed('f'):
            payload = {
                "topic": DEVICE_NAME,
                "message": "App On Device with topic " + DEVICE_NAME + " failed",
                "type": "appFail",
            }
            payload = json.dumps(payload)
            mqttClient.publish(mqttBrokerTopic, payload)
            print("Published App Fail") 
            while keyboard.is_pressed('p'):  # Wait for 'p' to be released
                time.sleep(0.1)
            time.sleep(0.5)
        # Add more key handling logic as needed
        if keyboard.is_pressed('q'):  # Press 'q' to quit
            print("Q was pressed, quitting.")
            break

mqtt_thread = threading.Thread(target=mqtt_client_thread)
mqtt_thread.start()

# Starting the keypress listener in a separate thread
keypress_thread = threading.Thread(target=keypress_thread)
keypress_thread.start()

# Wait for the keypress thread to finish
keypress_thread.join()
if mqttClient:
    mqttClient.loop_stop()
    mqttClient.disconnect()
print("Keypress thread finished. Exiting.")
exit(0)