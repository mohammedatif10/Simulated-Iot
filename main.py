import simpy
import networkx as nx
import random
from devices import Sensor, Actuator, Controller, MessageBroker

def sensor_process(env, sensor, broker):
    while True:
        data = sensor.generate_data()
        sensor.send_message(broker, (sensor.sensor_type, data), "Controller")
        yield env.timeout(10)

def main():
    env = simpy.Environment()
    broker = MessageBroker()

    sensors = [Sensor(i, random.choice(['temperature', 'humidity', 'motion'])) for i in range(1, 11)]
    actuators = [Actuator(i, random.choice(['light', 'lock', 'heater'])) for i in range(11, 16)]
    controllers = [Controller(i, actuators, broker) for i in range(16, 19)]

    for device in sensors + actuators + controllers:
        broker.subscribe(device, device.device_type)

    network = nx.Graph()
    for device in sensors + actuators + controllers:
        network.add_node(device.device_id, type=device.device_type)
        # Additional logic to add edges can be placed here

    for sensor in sensors:
        env.process(sensor_process(env, sensor, broker))

    env.run(until=100)

if __name__ == "__main__":
    main()
