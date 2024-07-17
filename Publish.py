import paho.mqtt.client as mqtt
import time
import grovepi
import math

# Sensor and actuator pins
temp_humidity_sensor = 7  # D7
sound_sensor = 0  # A0
ultrasonic_sensor = 4  # D4
pir_sensor = 8  # D8
light_sensor = 1  # A1
door_relay = 2  # D2
heater_led = 3  # D3
fan_led = 5  # D5

# MQTT broker details
mqttBroker = "192.168.0.100"  # Replace with the IP address of your MQTT broker
client = mqtt.Client("RaspberryPiPublisher")

def read_sensors():
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

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe("HEALTH_PDDL")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_publish(client, userdata, result):
    print("Data published.\n")
    pass

def on_message(client, userdata, message):
    s = str(message.payload.decode("utf-8"))
    print("Received action: ", s)
    action = eval(s)
    handle_actuation(action)

def handle_actuation(action):
    if action.get('light_action') == 'turn_on_light':
        grovepi.digitalWrite(light_sensor, 1)
    elif action.get('light_action') == 'turn_off_light':
        grovepi.digitalWrite(light_sensor, 0)

    if action.get('pressure_action') == 'turn_on_pressure':
        grovepi.digitalWrite(door_relay, 1)
    elif action.get('pressure_action') == 'turn_off_pressure':
        grovepi.digitalWrite(door_relay, 0)

    if action.get('temp_action') == 'turn_on_heater':
        grovepi.digitalWrite(heater_led, 1)
    elif action.get('temp_action') == 'turn_off_heater':
        grovepi.digitalWrite(heater_led, 0)

    if action.get('hum_action') == 'turn_on_humidity':
        grovepi.digitalWrite(fan_led, 1)
    elif action.get('hum_action') == 'turn_off_humidity':
        grovepi.digitalWrite(fan_led, 0)

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.connect(mqttBroker)

def main():
    while True:
        temp, hum, sound_level, distance, motion, light_intensity = read_sensors()

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

        mqtt_payload = str(payload_data)
        client.publish("HEALTH", mqtt_payload)
        print("Just published " + mqtt_payload + " to Topic HEALTH")

        time.sleep(5)

if __name__ == "__main__":
    main()
