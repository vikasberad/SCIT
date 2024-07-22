import paho.mqtt.client as mqtt
import json
import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess

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

# AI Planner
def run_planner(domain_file, problem_file):
    try:
        myCmd = f'python generate_plan.py {domain_file} {problem_file}'
        process = subprocess.Popen(myCmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        output = process.stdout.read().decode()
        actions = output.strip().split('\n')
        return actions
    except Exception as e:
        print("Error running AI planner: {}".format(e))
        return []

# Actuation function
def send_actuation(action, status):
    payload = json.dumps({action: status})
    client_gui.publish(actuation_topic, payload)

# Update functions
def update_gauges():
    gauge_temp["value"] = slider_temp.get() if use_slider_temp else data["Temperature"]
    label_temp_value.config(text=f"{gauge_temp['value']} °C")
    
    gauge_hum["value"] = slider_hum.get() if use_slider_hum else data["Humidity"]
    label_hum_value.config(text=f"{gauge_hum['value']} %")
    
    gauge_sound["value"] = data["Sound_Level"]
    label_sound_value.config(text=f"{data['Sound_Level']} dB")
    
    gauge_light["value"] = data["Light_intensity"]
    label_light_value.config(text=f"{data['Light_intensity']}")

    label_motion.config(text="Room Occupied" if data["Motion"] else "Room Empty")

    update_heater_fan_status()
    update_dehumidifier_status()
    update_sound_alert()
    update_light_alert()
    update_door_status()
    label_time.config(text=f"Current Time: {data['Time']}")

def update_heater_fan_status():
    current_time = time.time()
    motion_detected = last_motion_time and (current_time - last_motion_time <= 20)
    temperature = slider_temp.get() if use_slider_temp else data["Temperature"]

    if motion_detected:
        problem_file_content = f"""
        (define (problem temperature_problem)
          (:domain temperature_control)
          (:init {"(temp_low)" if temperature < 20 else ""} {"(temp_high)" if temperature > 25 else ""} (heater_off) (fan_off) (motion_detected))
          (:goal (and {"(fan_on)" if temperature > 25 else "(heater_on)"} {"(heater_off)" if temperature > 25 else "(fan_off)"}))
        )
        """
        with open("temperature_problem.pddl", "w") as f:
            f.write(problem_file_content)

        actions = run_planner("temperature_control.pddl", "temperature_problem.pddl")

        for action in actions:
            if action == "turn_on_heater":
                label_heater_status.config(text="Heater: ON")
                label_fan_status.config(text="Fan: OFF")
                send_actuation("temp_action", "turn_on_heater")
            elif action == "turn_on_fan":
                label_heater_status.config(text="Heater: OFF")
                label_fan_status.config(text="Fan: ON")
                send_actuation("temp_action", "turn_on_fan")
            elif action == "turn_off_heater":
                label_heater_status.config(text="Heater: OFF")
                send_actuation("temp_action", "turn_off_heater")
            elif action == "turn_off_fan":
                label_fan_status.config(text="Fan: OFF")
                send_actuation("temp_action", "turn_off_fan")
    else:
        label_heater_status.config(text="Heater: OFF")
        label_fan_status.config(text="Fan: OFF")
        send_actuation("temp_action", "turn_off_heater")
        send_actuation("temp_action", "turn_off_fan")

def update_dehumidifier_status():
    humidity = slider_hum.get() if use_slider_hum else data["Humidity"]
    if humidity > 60:
        label_dehumidifier_status.config(text="Dehumidifier: ON")
        send_actuation("hum_action", "turn_on_dehumidifier")
    else:
        label_dehumidifier_status.config(text="Dehumidifier: OFF")
        send_actuation("hum_action", "turn_off_dehumidifier")

def update_sound_alert():
    if data["Sound_Level"] > 250:
        label_sound_alert.config(text="Warning: It's too loud inside the office. Please be quiet!")
    else:
        label_sound_alert.config(text="")

def update_light_alert():
    if data["Light_intensity"] < 100:
        label_light_alert.config(text="Office lights ON")
    else:
        label_light_alert.config(text="Office lights OFF")

def update_door_status():
    if data["Distance"] < 10:
        label_door_status.config(text="Main Door: OPEN")
        send_actuation("door_action", "open_door")
    else:
        label_door_status.config(text="Main Door: CLOSED")
        send_actuation("door_action", "close_door")

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

# GUI setup
root = tk.Tk()
root.title("Sensor Data Dashboard")
root.geometry("800x600")
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

def create_frame(label, row, column, colspan=1):
    frame = ttk.LabelFrame(root, text=label)
    frame.grid(row=row, column=column, padx=10, pady=10, columnspan=colspan, sticky="nsew")
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

def create_gauge(frame, max_value):
    style = ttk.Style()
    style.configure("TProgressbar", thickness=20)
    gauge = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate", maximum=max_value, style="TProgressbar")
    gauge.pack(pady=5)
    label_value = ttk.Label(frame, text="0", font=("Helvetica", 10))
    label_value.pack(pady=5)
    return gauge, label_value

gauge_temp, label_temp_value = create_gauge(frame_temp, 50)
slider_temp = tk.Scale(frame_temp, from_=0, to=50, orient="horizontal", length=150)
slider_temp.pack()

gauge_hum, label_hum_value = create_gauge(frame_hum, 100)
slider_hum = tk.Scale(frame_hum, from_=0, to=100, orient="horizontal", length=150)
slider_hum.pack()

gauge_sound, label_sound_value = create_gauge(frame_sound, 150)
gauge_light, label_light_value = create_gauge(frame_light, 1023)

label_motion = ttk.Label(frame_motion, text="No Motion", font=("Helvetica", 10))
label_motion.pack(pady=5)

label_door_status = ttk.Label(frame_door, text="Door Closed", font=("Helvetica", 10))
label_door_status.pack(pady=5)

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

label_time = ttk.Label(frame_time, text="Current Time: ", font=("Helvetica", 10))
label_time.pack(pady=5)

toggle_temp = tk.Checkbutton(frame_temp, text="Use Slider Temp", command=lambda: toggle_slider("temp"))
toggle_temp.pack(pady=5)
toggle_hum = tk.Checkbutton(frame_hum, text="Use Slider Hum", command=lambda: toggle_slider("hum"))
toggle_hum.pack(pady=5)

def toggle_slider(sensor):
    global use_slider_temp, use_slider_hum
    if sensor == "temp":
        use_slider_temp = not use_slider_temp
    elif sensor == "hum":
        use_slider_hum = not use_slider_hum
    update_gauges()

def on_closing():
    disconnect_mqtt()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start MQTT in a separate thread to keep the GUI responsive
threading.Thread(target=connect_mqtt).start()

root.mainloop()
