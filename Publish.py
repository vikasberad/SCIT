import paho.mqtt.client as mqtt
import time
import grovepi
import math
import json

# Sensor and actuator pins
temp_humidity_sensor = 7  # D7
sound_sensor = 0  # A0
ultrasonic_sensor = 4  # D4
pir_sensor = 8  # D8
light_sensor = 1  # A1
door_relay = 2  # D2
heater_led = 3  # D3
fan_led = 5  # D5

# Threshold for ultrasonic sensor to open the door
DOOR_OPEN_DISTANCE_THRESHOLD = 10  # distance in cm

# MQTT broker details
mqttBroker = "broker.hivemq.com"  # Public broker address
client = mqtt.Client("RaspberryPiPublisher")

def read_sensors():
    try:
        # Reading temperature and humidity
        [temp, hum] = grovepi.dht(temp_humidity_sensor, 0)
        if math.isnan(temp) or math.isnan(hum):
            temp, hum = 0.0, 0.0

        # Reading sound level
        sound_level = grovepi.analogRead(sound_sensor)

        # Reading distance from ultrasonic sensor
        distance = grovepi.ultrasonicRead(ultrasonic_sensor)

        # Reading motion from PIR sensor
        motion = grovepi.digitalRead(pir_sensor)

        # Reading light intensity
        light_intensity = grovepi.analogRead(light_sensor)

        return temp, hum, sound_level, distance, motion, light_intensity
    except Exception as e:
        print("Error reading sensors: {}".format(e))
        return 0.0, 0.0, 0, 0, 0, 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe("HEALTH_PDDL")
    else:
        print("Failed to connect, return code {}\n".format(rc))

def on_publish(client, userdata, result):
    print("Data published.\n")
    pass

def on_message(client, userdata, message):
    try:
        s = str(message.payload.decode("utf-8"))
        print("Received action: ", s)
        action = eval(s)
        handle_actuation(action)
    except Exception as e:
        print("Error handling message: {}".format(e))

def handle_actuation(action):
    try:
        if action.get('light_action') == 'turn_on_light':
            grovepi.digitalWrite(light_sensor, 1)
        elif action.get('light_action') == 'turn_off_light':
            grovepi.digitalWrite(light_sensor, 0)

        if action.get('door_action') == 'open_door':
            grovepi.digitalWrite(door_relay, 1)
        elif action.get('door_action') == 'close_door':
            grovepi.digitalWrite(door_relay, 0)

        if action.get('temp_action') == 'turn_on_heater':
            grovepi.digitalWrite(heater_led, 1)
        elif action.get('temp_action') == 'turn_off_heater':
            grovepi.digitalWrite(heater_led, 0)

        if action.get('hum_action') == 'turn_on_fan':
            grovepi.digitalWrite(fan_led, 1)
        elif action.get('hum_action') == 'turn_off_fan':
            grovepi.digitalWrite(fan_led, 0)
    except Exception as e:
        print("Error handling actuation: {}".format(e))

def main():
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message

    print("Connecting to MQTT broker at {}...".format(mqttBroker))
    try:
        client.connect(mqttBroker, 1883, 60)
    except Exception as e:
        print("Connection failed: {}".format(e))
        return

    client.loop_start()

    while True:
        try:
            temp, hum, sound_level, distance, motion, light_intensity = read_sensors()

            # Logic for opening the door based on ultrasonic sensor
            if distance <= DOOR_OPEN_DISTANCE_THRESHOLD:
                print("Distance is within threshold, opening door.")
                grovepi.digitalWrite(door_relay, 1)  # Open door
            else:
                grovepi.digitalWrite(door_relay, 0)  # Close door

            # Prepare the payload data
            payload_data = {
                "Temperature": temp,
                "Humidity": hum,
                "Sound_Level": sound_level,
                "Distance": distance,
                "Motion": motion,
                "Light_intensity": light_intensity,
                "Time": time.strftime('%Y-%m-%d %H:%M:%S')
            }

            mqtt_payload = json.dumps(payload_data)
            client.publish("HEALTH", mqtt_payload)
            print("Just published " + mqtt_payload + " to Topic HEALTH")

        except Exception as e:
            print("Error reading sensors or publishing: {}".format(e))

        time.sleep(1)

if __name__ == "__main__":
    main()
