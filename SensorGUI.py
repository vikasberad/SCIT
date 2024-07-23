import paho.mqtt.client as mqtt
import json
import tkinter as tk
from tkinter import ttk
import threading
import time

# MQTT broker details
mqttBroker = "broker.hivemq.com"
topic = "HEALTH"
actuation_topic = "HEALTH_PDDL"

# Data storage
data = {
    "Temperature": 0,
    "Humidity": 0,
    "Sound_Level": 0,
    "Distance": 0,
    "Light_intensity": 0,
    "Motion": 0,
    "Time": ""
}

# MQTT client
client_gui = mqtt.Client("PythonGUI")

# Timestamps for motion detection
last_motion_time = None

# Flags for demo mode
use_slider_temp = False
use_slider_hum = False

# GUI setup
root = tk.Tk()
root.title("Sensor Data Dashboard")
root.geometry("1000x700")  # Set the initial window size

# MQTT functions
def on_message(client, userdata, message):
    global last_motion_time
    payload = json.loads(message.payload.decode("utf-8"))
    print("Received message:", payload)

    data["Temperature"] = payload["Temperature"]
    data["Humidity"] = payload["Humidity"]
    data["Sound_Level"] = payload["Sound_Level"]
    data["Distance"] = payload["Distance"]
    data["Light_intensity"] = payload["Light_intensity"]
    data["Motion"] = payload["Motion"]
    data["Time"] = payload["Time"]

    if data["Motion"] == 1:
        last_motion_time = time.time()

    update_gauges()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic)
    else:
        print("Failed to connect, return code {}\n".format(rc))

client_gui.on_connect = on_connect
client_gui.on_message = on_message

def connect_mqtt():
    client_gui.connect(mqttBroker, keepalive=60)
    client_gui.loop_start()

def disconnect_mqtt():
    client_gui.loop_stop()

# GUI layout
def create_frame(label, row, col, colspan=1):
    frame = ttk.LabelFrame(root, text=label)
    frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew", columnspan=colspan)
    return frame

frame_temp = create_frame("Temperature", 0, 0)
frame_hum = create_frame("Humidity", 0, 1)
frame_sound = create_frame("Sound Level", 1, 0)
frame_light = create_frame("Light Intensity", 1, 1)
frame_motion = create_frame("Motion", 2, 0)
frame_door = create_frame("Door Status", 2, 1)
frame_heater_fan = create_frame("Heater/Fan Status", 3, 0, colspan=2)
frame_dehumidifier = create_frame("Dehumidifier Status", 4, 0, colspan=2)
frame_sound_alert = create_frame("Sound Alert", 5, 0, colspan=2)
frame_light_alert = create_frame("Light Alert", 6, 0, colspan=2)
frame_time = create_frame("Current Time", 7, 0, colspan=2)

style = ttk.Style()
style.configure("TProgressbar", thickness=20)

def create_gauge(frame, max_value):
    gauge = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate", maximum=max_value, style="TProgressbar")
    gauge.pack(pady=5)
    label = ttk.Label(frame, text="0", font=("Helvetica", 10))
    label.pack(pady=5)
    return gauge, label

gauge_temp, label_temp_value = create_gauge(frame_temp, 50)
gauge_hum, label_hum_value = create_gauge(frame_hum, 100)
gauge_sound, label_sound_value = create_gauge(frame_sound, 150)
gauge_light, label_light_value = create_gauge(frame_light, 1023)

label_motion = ttk.Label(frame_motion, text="Room Empty", font=("Helvetica", 10))
label_motion.pack(pady=10)

label_door_status = ttk.Label(frame_door, text="Door Closed", font=("Helvetica", 10))
label_door_status.pack(pady=10)

label_heater_status = ttk.Label(frame_heater_fan, text="Heater: OFF", font=("Helvetica", 10))
label_heater_status.pack(pady=5)
label_fan_status = ttk.Label(frame_heater_fan, text="Fan: OFF", font=("Helvetica", 10))
label_fan_status.pack(pady=5)

label_dehumidifier_status = ttk.Label(frame_dehumidifier, text="Dehumidifier: OFF", font=("Helvetica", 10))
label_dehumidifier_status.pack(pady=5)

label_sound_alert = ttk.Label(frame_sound_alert, text="", font=("Helvetica", 10), foreground="red")
label_sound_alert.pack(pady=5)

label_light_alert = ttk.Label(frame_light_alert, text="", font=("Helvetica", 10), foreground="blue")
label_light_alert.pack(pady=5)

label_time = ttk.Label(frame_time, text="", font=("Helvetica", 10))
label_time.pack(pady=5)

def update_gauges():
    gauge_temp["value"] = slider_temp.get() if use_slider_temp else data["Temperature"]
    label_temp_value.config(text=f"{gauge_temp['value']} °C")
    
    gauge_hum["value"] = slider_hum.get() if use_slider_hum else data["Humidity"]
    label_hum_value.config(text=f"{gauge_hum['value']} %")
    
    gauge_sound["value"] = data["Sound_Level"]
    label_sound_value.config(text=f"{data['Sound_Level']} dB")
    
    gauge_light["value"] = data["Light_intensity"]
    label_light_value.config(text=f"{data['Light_intensity']}")

    current_time = time.time()
    motion_detected = last_motion_time and (current_time - last_motion_time <= 20)
    label_motion.config(text="Room Occupied" if motion_detected else "Room Empty")

    update_heater_fan_status()
    update_dehumidifier_status()
    update_sound_alert()
    update_light_alert()
    update_door_status()
    label_time.config(text=f"Current Time: {data['Time']}")

def send_actuation(action, status):
    payload = json.dumps({action: status})
    client_gui.publish(actuation_topic, payload)
    print(f"Sent {action} {status}")

def update_heater_fan_status():
    current_time = time.time()
    motion_detected = last_motion_time and (current_time - last_motion_time <= 20)
    temperature = slider_temp.get() if use_slider_temp else data["Temperature"]

    if motion_detected:
        if temperature < 20:
            label_heater_status.config(text="Heater: ON")
            label_fan_status.config(text="Fan: OFF")
            send_actuation('temp_action', 'turn_on_heater')
            send_actuation('fan_action', 'turn_off_fan')
        elif temperature > 25:
            label_heater_status.config(text="Heater: OFF")
            label_fan_status.config(text="Fan: ON")
            send_actuation('temp_action', 'turn_off_heater')
            send_actuation('fan_action', 'turn_on_fan')
        else:
            label_heater_status.config(text="Heater: OFF")
            label_fan_status.config(text="Fan: OFF")
            send_actuation('temp_action', 'turn_off_heater')
            send_actuation('fan_action', 'turn_off_fan')
    else:
        label_heater_status.config(text="Heater: OFF")
        label_fan_status.config(text="Fan: OFF")
        send_actuation('temp_action', 'turn_off_heater')
        send_actuation('fan_action', 'turn_off_fan')

def update_dehumidifier_status():
    humidity = slider_hum.get() if use_slider_hum else data["Humidity"]
    if humidity > 60:
        label_dehumidifier_status.config(text="Dehumidifier: ON")
        send_actuation('hum_action', 'turn_on_dehumidifier')
    else:
        label_dehumidifier_status.config(text="Dehumidifier: OFF")
        send_actuation('hum_action', 'turn_off_dehumidifier')

def update_sound_alert():
    if data["Sound_Level"] > 250:
        label_sound_alert.config(text="Warning: It's too loud inside the office. Please be quiet!")
    else:
        label_sound_alert.config(text="")

def update_light_alert():
    if data["Light_intensity"] < 100:
        label_light_alert.config(text="Office lights ON")
        send_actuation('light_action', 'turn_on_light')
    else:
        label_light_alert.config(text="Office lights OFF")
        send_actuation('light_action', 'turn_off_light')

def update_door_status():
    if data["Distance"] < 10:
        label_door_status.config(text="Main Door: OPEN")
    else:
        label_door_status.config(text="Main Door: CLOSED")

def toggle_temp():
    global use_slider_temp
    use_slider_temp = not use_slider_temp
    if use_slider_temp:
        button_toggle_temp.config(text="Use Real Temperature Data")
    else:
        button_toggle_temp.config(text="Use Slider Temperature Data")
    update_gauges()

def toggle_hum():
    global use_slider_hum
    use_slider_hum = not use_slider_hum
    if use_slider_hum:
        button_toggle_hum.config(text="Use Real Humidity Data")
    else:
        button_toggle_hum.config(text="Use Slider Humidity Data")
    update_gauges()

frame_slider_temp = create_frame("Temperature Slider", 0, 2)
slider_temp = tk.Scale(frame_slider_temp, from_=0, to=50, orient="horizontal")
slider_temp.pack(padx=5, pady=5)
button_toggle_temp = ttk.Button(frame_slider_temp, text="Use Slider Temperature Data", command=toggle_temp)
button_toggle_temp.pack(padx=5, pady=5)

frame_slider_hum = create_frame("Humidity Slider", 1, 2)
slider_hum = tk.Scale(frame_slider_hum, from_=0, to=100, orient="horizontal")
slider_hum.pack(padx=5, pady=5)
button_toggle_hum = ttk.Button(frame_slider_hum, text="Use Slider Humidity Data", command=toggle_hum)
button_toggle_hum.pack(padx=5, pady=5)

def on_closing():
    disconnect_mqtt()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start MQTT in a separate thread to keep the GUI responsive
threading.Thread(target=connect_mqtt).start()

root.mainloop()
