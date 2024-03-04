# For each file in all the folders, take the mqttReceiver.py file and generate
# instance of it in the same folder. It should be generated for each .json file
# in the same folder. The generated file should be named as the .json file.
# Also replace the deviceName, mqttBrokerTopic, mqttBrokerIP, mqttBrokerPort, app_path, app_name variables
# with the values from the .json file. The .json file should contain the same
# variables as the mqttReceiver.py file.

import os
import json
import shutil
import re

keys = ['DEVICE_NAME', 'MQTT_BROKER_TOPIC', 'MQTT_BROKER_IP', 'MQTT_BROKER_PORT', 'APP_PATH', 'APP_NAME']

def generate_instance(file, json_file):
    with open(file, 'r') as f:
        file_content = f.read()
        with open(json_file, 'r') as jf:
            name = os.path.splitext(os.path.basename(json_file))[0]
            json_content = json.load(jf)
            for key in keys:
                file_content = re.sub(key, json_content[key], file_content)
            new_file = os.path.join(os.path.dirname(json_file), name + '.py')
            with open(new_file, 'w') as nf:
                nf.write(file_content)
            print('Generated instance: ' + new_file)

def main():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.json'):
                json_file = os.path.join(root, file)
                generate_instance('mqttReceiver.py', json_file)

if __name__ == '__main__':
    main()