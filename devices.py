import random

class IoTDevice:
    def __init__(self, device_id, device_type):
        self.device_id = device_id
        self.device_type = device_type

    def send_message(self, broker, message, target_device_type):
        broker.publish(self, message, target_device_type)

    def receive_message(self, sender, message):
        print(f"{self.device_type} {self.device_id} received message from {sender.device_type} {sender.device_id}: {message}")

class Sensor(IoTDevice):
    def __init__(self, device_id, sensor_type):
        super().__init__(device_id, "Sensor")
        self.sensor_type = sensor_type

    def generate_data(self):
        if self.sensor_type == 'temperature':
            return f"Temperature: {random.randint(15, 30)}°C"
        elif self.sensor_type == 'humidity':
            return f"Humidity: {random.randint(30, 90)}%"
        elif self.sensor_type == 'motion':
            return f"Motion detected: {random.choice([True, False])}"
        else:
            return "Unknown data"

class Actuator(IoTDevice):
    def __init__(self, device_id, actuator_type):
        super().__init__(device_id, "Actuator")
        self.actuator_type = actuator_type

    def perform_action(self, command):
        print(f"Actuator {self.actuator_type} {self.device_id} performing action: {command}")

class Controller(IoTDevice):
    def __init__(self, device_id, actuators, broker):
        super().__init__(device_id, "Controller")
        self.actuators = actuators
        self.broker = broker

    def receive_message(self, sender, message):
        super().receive_message(sender, message)
        sensor_type, data = message
        action = self.process_data(sensor_type, data)
        for actuator in self.actuators:
            self.broker.send_direct_message(self, action, actuator)

    def process_data(self, sensor_type, data):
        if sensor_type == 'temperature':
            temperature_value = int(data.split(":")[1].strip().strip("°C"))
            if temperature_value > 25:
                return "Turn on AC"
        elif sensor_type == 'motion':
            motion_detected = data.split(":")[1].strip()
            if motion_detected == "True":
                return "Turn on lights"
        else:
            return "No action"

class MessageBroker:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, device, device_type):
        if device_type not in self.subscriptions:
            self.subscriptions[device_type] = []
        self.subscriptions[device_type].append(device)

    def publish(self, sender, message, target_device_type):
        for device in self.subscriptions.get(target_device_type, []):
            device.receive_message(sender, message)

    def send_direct_message(self, sender, message, recipient):
        recipient.receive_message(sender, message)
