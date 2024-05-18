import random

class IoTDevice:
    def __init__(self, device_id, device_type, broker):
        self.device_id = device_id
        self.device_type = device_type
        self.broker = broker

    def connect(self):
        self.broker.subscribe(self, self.device_type)
        print(f"{self.device_type} {self.device_id} connected to the network.")

    def disconnect(self):
        self.broker.unsubscribe(self, self.device_type)
        print(f"{self.device_type} {self.device_id} disconnected from the network.")

    def send_message(self, message, target_device_type):
        self.broker.publish(self, message, target_device_type)

    def receive_message(self, sender, message):
        print(f"{self.device_type} {self.device_id} received message from {sender.device_type} {sender.device_id}: {message}")

class Sensor(IoTDevice):
    def __init__(self, device_id, sensor_type, broker):
        super().__init__(device_id, "Sensor", broker)
        self.sensor_type = sensor_type

    def generate_data(self):
        import random
        if self.sensor_type == 'temperature':
            return f"Temperature: {random.uniform(15.0, 30.0):.2f}°C"
        elif self.sensor_type == 'humidity':
            return f"Humidity: {random.uniform(30.0, 90.0):.2f}%"
        elif self.sensor_type == 'motion':
            return f"Motion detected: {random.choice([True, False])}"

class Actuator(IoTDevice):
    def __init__(self, device_id, actuator_type, broker):
        super().__init__(device_id, "Actuator", broker)
        self.actuator_type = actuator_type

    def perform_action(self, command):
        print(f"Actuator {self.actuator_type} {self.device_id} performing action: {command}")

class Controller(IoTDevice):
    def __init__(self, device_id, actuators, broker):
        super().__init__(device_id, "Controller", broker)
        self.actuators = actuators

    def receive_message(self, sender, message):
        super().receive_message(sender, message)
        sensor_type, data = message.split(',', 1)
        action = self.process_data(sensor_type, data)
        for actuator in self.actuators:
            self.broker.send_direct_message(self, action, actuator)

    def process_data(self, sensor_type, data):
        if sensor_type == 'temperature':
            temperature_value = float(data.split(':')[1].strip().replace('°C', ''))
            if temperature_value > 25.0:
                return "Turn on AC"
        elif sensor_type == 'motion':
            motion_detected = data.split(':')[1].strip()
            if motion_detected == "True":
                return "Turn on lights"
        return "No action"

class MessageBroker:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, device, device_type):
        if device_type not in self.subscriptions:
            self.subscriptions[device_type] = []
        self.subscriptions[device_type].append(device)

    def unsubscribe(self, device, device_type):
        if device_type in self.subscriptions:
            self.subscriptions[device_type].remove(device)
            if not self.subscriptions[device_type]:
                del self.subscriptions[device_type]

    def publish(self, sender, message, target_device_type):
        for device in self.subscriptions.get(target_device_type, []):
            device.receive_message(sender, message)

    def send_direct_message(self, sender, message, recipient):
        recipient.receive_message(sender, message)
