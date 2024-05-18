import time

class IoTDevice:
    def __init__(self, device_id, device_type):
        self.device_id = device_id
        self.device_type = device_type
        self.connected = True

    def connect(self):
        self.connected = True
        print(f"{self.device_type} {self.device_id} connected.")

    def disconnect(self):
        self.connected = False
        print(f"{self.device_type} {self.device_id} disconnected.")

    def send_message(self, broker, message, target_device_type):
        if self.connected:
            print(f"{self.device_type} {self.device_id} sending message: {message}")
            broker.publish(self, message, target_device_type)

    def receive_message(self, sender, message):
        if self.connected:
            print(f"{self.device_type} {self.device_id} received message from {sender.device_type} {sender.device_id}: {message}")

class Sensor(IoTDevice):
    def __init__(self, device_id, sensor_type, broker):
        super().__init__(device_id, "Sensor")
        self.sensor_type = sensor_type
        self.broker = broker

    def generate_data(self):
        import random
        if self.sensor_type == 'temperature':
            return f"Temperature: {random.randint(15, 30)}°C"
        elif self.sensor_type == 'humidity':
            return f"Humidity: {random.randint(30, 90)}%"
        elif self.sensor_type == 'motion':
            return f"Motion detected: {random.choice([True, False])}"

    def send_message(self, message, target_device_type):
        super().send_message(self.broker, message, target_device_type)

class Actuator(IoTDevice):
    def __init__(self, device_id, actuator_type, broker):
        super().__init__(device_id, "Actuator")
        self.actuator_type = actuator_type
        self.broker = broker

    def perform_action(self, command):
        print(f"Actuator {self.actuator_type} {self.device_id} performing action: {command}")

class Controller(IoTDevice):
    def __init__(self, device_id, actuators, broker):
        super().__init__(device_id, "Controller")
        self.actuators = actuators
        self.broker = broker

    def receive_message(self, sender, message):
        if self.connected:
            super().receive_message(sender, message)
            sensor_type, data = message.split(',', 1)
            action = self.process_data(sensor_type, data)
            for actuator in self.actuators:
                self.broker.send_direct_message(self, action, actuator)

    def process_data(self, sensor_type, data):
        if sensor_type == 'temperature':
            temperature_value = int(data.split(':')[1].strip().replace('°C', ''))
            if temperature_value > 25:
                return "Turn on AC"
        elif sensor_type == 'motion':
            motion_detected = data.split(':')[1].strip()
            if motion_detected == "True":
                return "Turn on lights"
        return "No action"

class MessageBroker:
    def __init__(self):
        self.subscriptions = {}
        self.message_log = []

    def subscribe(self, device, device_type):
        if device_type not in self.subscriptions:
            self.subscriptions[device_type] = []
        self.subscriptions[device_type].append(device)

    def publish(self, sender, message, target_device_type):
        log_entry = {
            'sender_id': sender.device_id,
            'sender_type': sender.device_type,
            'message': message,
            'message_size': len(message),
            'timestamp': time.time()
        }
        for device in self.subscriptions.get(target_device_type, []):
            log_entry['recipient_id'] = device.device_id
            log_entry['recipient_type'] = device.device_type
            self.message_log.append(log_entry.copy())
            device.receive_message(sender, message)

    def send_direct_message(self, sender, message, recipient):
        log_entry = {
            'sender_id': sender.device_id,
            'sender_type': sender.device_type,
            'recipient_id': recipient.device_id,
            'recipient_type': recipient.device_type,
            'message': message,
            'message_size': len(message),
            'timestamp': time.time()
        }
        self.message_log.append(log_entry)
        recipient.receive_message(sender, message)

    def get_message_log(self):
        return self.message_log
