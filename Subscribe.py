import paho.mqtt.client as mqtt
import time
import os
import ast

# Setpoints
light_sp = 300
temp_sp = 30
pressure_sp = 25
humidity_sp = 40

# MQTT broker details
mqttBroker = "192.168.0.100"  # Replace with the IP address of your MQTT broker
client = mqtt.Client("RemoteSubscriber")

# Parse the output file from AI planner
def parseFile(filename):
    with open(filename, 'r+') as f:
        lines = f.readlines()
    print("F.PRINTLINE IS", lines, len(lines))
    action1 = lines[0].strip().split()[0]
    print(action1)
    return action1

# Run the AI planner
def run_planner(domainname, problem, out):
    myCmd = 'python ai_planner_2.py {0} {1} {2}'.format(domainname, problem, out)
    os.system(myCmd)
    action = parseFile(out)
    return action

# Callback when a message is received from the broker
def on_message(client, userdata, message):
    s = str(message.payload.decode("utf-8"))
    print("Received message: ", s)
    payload_data = eval(s)
    print("Payload data: ", payload_data)
    
    excel_data = {'Time': None, 'Temperature': None, 'Humidity': None, 'Pressure': None, 'Motion': None, 'Alert': None, 'Light_intensity': None}
    
    for key in excel_data.keys():
        if key in payload_data:
            excel_data[key] = payload_data[key]
    
    print("Excel data: ", excel_data)

    # Initialize action variables
    light_action = None
    pressure_action = None
    temp_action = None
    hum_action = None

    # Light_intensity PDDL
    domain = 'Light_intensity_Domain.pddl'
    filename = 'light_plan.txt'
    if excel_data['Light_intensity'] < light_sp:
        problem = 'Light_intensity_HighProb.pddl'
        print("ON plan created")
    else:
        problem = 'Light_intensity_LowProb.pddl'
        print("OFF plan created")
    light_action = run_planner(domain, problem, filename)

    # Pressure PDDL
    domain = 'Pressure_Domain.pddl'
    filename = 'pressure_plan.txt'
    if excel_data['Pressure'] < pressure_sp:
        problem = 'Pressure_HighProb.pddl'
        print("ON plan created")
    else:
        problem = 'Pressure_LowProb.pddl'
        print("OFF plan created")
    pressure_action = run_planner(domain, problem, filename)

    # Temperature PDDL
    domain = 'Temp_Domain.pddl'
    filename = 'temp_plan.txt'
    if excel_data['Temperature'] > temp_sp:
        problem = 'Temp_HighProb.pddl'
        print("ON plan created")
    else:
        problem = 'Temp_LowProb.pddl'
        print("OFF plan created")
    temp_action = run_planner(domain, problem, filename)
  
    # Humidity PDDL
    domain = 'Hum_Domain.pddl'
    filename = 'hum_plan.txt'
    if excel_data['Humidity'] > humidity_sp:
        problem = 'Hum_HighProb.pddl'
        print("OFF plan created")
    else:
        problem = 'Hum_LowProb.pddl'
        print("ON plan created")
    hum_action = run_planner(domain, problem, filename)

    # Combine actions
    action = {
        'light_action': light_action,
        'pressure_action': pressure_action,
        'temp_action': temp_action,
        'hum_action': hum_action
    }

    # Publish actions back to Raspberry Pi
    mqtt_payload = str(action)
    print(mqtt_payload)
    client.publish("HEALTH_PDDL", mqtt_payload)
    print("Just published " + mqtt_payload + " to Topic HEALTH_PDDL")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code " + str(rc))
        client.subscribe("HEALTH")
    else:
        print("Failed to connect, return code %d\n", rc)

# Create a MQTT client instance
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttBroker)

# Start the loop to process received messages
client.loop_forever()
