# mock_grovepi.py

def dht(pin, module_type):
    return (25.0, 50.0)  # Return some dummy temperature and humidity values

def analogRead(pin):
    return 300  # Return some dummy sensor value

def ultrasonicRead(pin):
    return 15  # Return some dummy distance value

def digitalRead(pin):
    return 1  # Return some dummy motion value

def digitalWrite(pin, value):
    print(f"Setting pin {pin} to {value}")
