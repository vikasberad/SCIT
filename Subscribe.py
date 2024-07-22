import paho.mqtt.client as mqtt
import os
import subprocess
import json

# Setpoints
light_sp = 300
temp_sp_high = 25
temp_sp_low = 20
humidity_sp = 40

# MQTT broker details
mqttBroker = "broker.hivemq.com"  # Public broker address
client = mqtt.Client("RemoteSubscriber", protocol=mqtt.MQTTv311)

# Run the AI planner
def run_planner(domain, problem):
    try:
        myCmd = f'python generate_plan.py {domain} {problem}'
        process = subprocess.Popen(myCmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        output = process.stdout.read().decode()
        actions = output.strip().split('\n')
        return actions
    except Exception as e:
        print("Error running AI planner: {}".format(e))
        return []

# Callback when a message is received from the broker
def on_message(client, userdata, message):
    try:
        s = str(message.payload.decode("utf-8"))
        print("Received message: ", s)
        payload_data = json.loads(s)
        print("Payload data: ", payload_data)

        excel_data = {
            'Time': payload_data.get('Time', ''),
            'Temperature': payload_data.get('Temperature', 0.0),
            'Humidity': payload_data.get('Humidity', 0.0),
            'Motion': payload_data.get('Motion', 0),
            'Light_intensity': payload_data.get('Light_intensity', 0),
            'Alert': None
        }

        print("Excel data: ", excel_data)

        # Generate the plan
        domain = 'combined_domain.pddl'
        problem = 'combined_problem.pddl'
        actions = run_planner(domain, problem)
        print("Generated Plan: ", actions)

        # Prepare the actions to publish
        action_dict = {'light_action': None, 'temp_action': None, 'hum_action': None}
        for action in actions:
            if 'turn_on_light' in action:
                action_dict['light_action'] = 'turn_on_light'
            elif 'turn_off_light' in action:
                action_dict['light_action'] = 'turn_off_light'
            elif 'turn_on_heater' in action:
                action_dict['temp_action'] = 'turn_on_heater'
            elif 'turn_off_heater' in action:
                action_dict['temp_action'] = 'turn_off_heater'
            elif 'turn_on_fan' in action:
                action_dict['temp_action'] = 'turn_on_fan'
            elif 'turn_off_fan' in action:
                action_dict['temp_action'] = 'turn_off_fan'
            elif 'turn_on_dehumidifier' in action:
                action_dict['hum_action'] = 'turn_on_dehumidifier'
            elif 'turn_off_dehumidifier' in action:
                action_dict['hum_action'] = 'turn_off_dehumidifier'

        # Publish actions back to Raspberry Pi
        mqtt_payload = json.dumps(action_dict)
        print(mqtt_payload)
        client.publish("HEALTH", mqtt_payload)
        print("Just published " + mqtt_payload + " to Topic HEALTH")
    except Exception as e:
        print("Error processing message: {}".format(e))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code " + str(rc))
        client.subscribe("HEALTH")
    else:
        print("Failed to connect, return code {}\n".format(rc))

# Create a MQTT client instance
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttBroker)

# Start the loop to process received messages
client.loop_forever()
