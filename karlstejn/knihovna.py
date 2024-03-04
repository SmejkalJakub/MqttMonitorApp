# Get Message From mqtt and send mqtt message after receiving
# How to use: python3 mqttReceiver.py [mqttBrokerIP] [mqttBrokerPort] [mqttBrokerTopic]
# Example: python3 mqttReceiver.py

import threading
import paho.mqtt.client as mqtt
import json
import os
import keyboard
import time
import subprocess
import time
import psutil
from ctypes import windll, c_ulong, byref

deviceName = "tablet/knihovna"
mqttBrokerTopic = "building/karlstejn/device/status"
mqttBrokerIP = "192.168.1.105"
mqttBrokerPort = 1883
topicSubscribe = deviceName + "/#"

app_path = "F:\\OneDrive\\Desktop\\OverlookTestCloud\\Overlook.exe"
app_name = "Overlook.exe"

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

def get_foreground_window_process_name():
    # Get the handle of the foreground window
    hwnd = windll.user32.GetForegroundWindow()
    pid = c_ulong(0)
    windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
    
    try:
        # Get the process name based on the PID
        return psutil.Process(pid.value).name()
    except psutil.NoSuchProcess:
        return None

def app_checker_thread():
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() == app_name.lower():
            process.kill()  # Close the specific app
            process.wait()  # Optional: Wait for the app to fully exit

    # Reopen the specific app
    subprocess.Popen(app_path)

    time.sleep(15)
    
    while True:
        if(keyboard.is_pressed('q')):
            print("Q was pressed, quitting.")
            break

        foreground_process_name = get_foreground_window_process_name()
        if foreground_process_name and foreground_process_name.lower() != app_name.lower():
            for process in psutil.process_iter(['name']):
                if process.info['name'].lower() == app_name.lower():
                    process.kill()  # Close the specific app
                    process.wait()  # Optional: Wait for the app to fully exit

            # Reopen the specific app
            subprocess.Popen(app_path)

            payload = {
                "topic": deviceName,
                "message": "Aplikace na zařízení " + deviceName + " selhala",
                "type": "appFail",
            }
            payload = json.dumps(payload)
            mqttClient.publish(mqttBrokerTopic, payload)
            print("Published App Fail") 

            # Wait for app to start
            time.sleep(3)

        # Check every second
        time.sleep(1)

def mqtt_client_thread():
    global mqttClient

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        payload = {
            "topic": deviceName,
            "message": "Zařízení " + deviceName + " připojeno k brokeru",
            "type": "info",
        }
        payload = json.dumps(payload)
        mqttClient.publish(mqttBrokerTopic, payload)

    def on_message(client, userdata, msg):
        # Check if topic ends in /shutdown
        if msg.topic.endswith("/shutdown"):
            print("Shutting down")
            payload = {
                "topic": deviceName,
                "message": "Zařízení " + deviceName + " vypnuto uživatelem",
                "type": "shutdown"
            }
            payload = json.dumps(payload)
            mqttClient.publish(mqttBrokerTopic, payload)
            shutdown_computer()
        elif msg.topic.endswith("/reboot"):
            print("Rebooting")
            payload = {
                "topic": deviceName,
                "message": "Zařízení " + deviceName + " restartováno uživatelem",
                "type": "reboot"
            }
            payload = json.dumps(payload)
            mqttClient.publish(mqttBrokerTopic, payload)
            reboot_computer()     

    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqttClient.connect(mqttBrokerIP, mqttBrokerPort, 60)
    mqttClient.subscribe(topicSubscribe, 0)

    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message

    mqttClient.loop_start()

mqtt_thread = threading.Thread(target=mqtt_client_thread)
mqtt_thread.start()

# Starting the app checker in a separate thread
app_checker_thread = threading.Thread(target=app_checker_thread)
app_checker_thread.start()

# Wait for the app checker thread to finish
app_checker_thread.join()
if mqttClient:
    mqttClient.loop_stop()
    mqttClient.disconnect()
print("Keypress thread finished. Exiting.")
exit(0)