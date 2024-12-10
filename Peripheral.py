import random

class Peripheral:
    def __init__(self):
        self.devices = {
            "LED1": {"state": 0, "value": None},
            "LED2": {"state": 0, "value": None},
            "LED3": {"state": 0, "value": None},
            "Fan1": {"state": 0, "value": None},
            "Fan2": {"state": 0, "value": None},
            "Fan3": {"state": 0, "value": None}
        }
        self.display = ""

    def control_device(self, device, state, value=None):
        if device in self.devices:
            self.devices[device]["state"] = state
            self.devices[device]["value"] = value
            status = f"{device} {'ON' if state else 'OFF'}"
            if value is not None:
                status += f" (Value: {value})"
            print(status)
        else:
            print("Unknown device")

    def update_display(self, message):
        self.display = message
        print(f"Display: {message}")

    def query_status(self, device):
        if device in self.devices:
            state = "ON" if self.devices[device]["state"] else "OFF"
            value = self.devices[device]["value"]
            if value is not None:
                return f"{device} is {state} with Value: {value}"
            return f"{device} is {state}"
        return "Unknown Device"

    def check_device_status(self, device):
        # Simulate random faults
        return "Faulty" if random.randint(0, 10) > 8 else "Normal"
