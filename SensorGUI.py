import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json

# MQTT settings
mqtt_broker = "broker.hivemq.com"
mqtt_topic = "HEALTH"

# Initialize the root window first
root = tk.Tk()

# Initialize global variables for sensor data
sensor_data = {
    "Temperature": tk.DoubleVar(root),
    "Humidity": tk.DoubleVar(root),
    "Sound_Level": tk.DoubleVar(root),
    "Distance": tk.DoubleVar(root),
    "Motion": tk.IntVar(root),
    "Light_intensity": tk.DoubleVar(root)
}

# MQTT client setup
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("Received message:", data)
    # Update sensor data variables
    sensor_data["Temperature"].set(data.get("Temperature", 0))
    sensor_data["Humidity"].set(data.get("Humidity", 0))
    sensor_data["Sound_Level"].set(data.get("Sound_Level", 0))
    sensor_data["Distance"].set(data.get("Distance", 0))
    sensor_data["Motion"].set(data.get("Motion", 0))
    sensor_data["Light_intensity"].set(data.get("Light_intensity", 0))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker)

# GUI setup
class SensorGUI(tk.Tk):
    def __init__(self, root):
        super().__init__()
        self.title("Sensor Data Monitor")

        # Create and place labels and data fields for each sensor
        row = 0
        for key, var in sensor_data.items():
            ttk.Label(self, text=key).grid(row=row, column=0, padx=10, pady=5, sticky="W")
            ttk.Label(self, textvariable=var).grid(row=row, column=1, padx=10, pady=5, sticky="E")
            row += 1

        # Start the MQTT client loop
        self.after(1000, self.mqtt_loop)

    def mqtt_loop(self):
        client.loop_start()
        self.after(1000, self.mqtt_loop)

if __name__ == "__main__":
    app = SensorGUI(root)
    app.mainloop()
