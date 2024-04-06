import simpy
import networkx as nx
from devices import Sensor, Actuator, Controller, generate_devices

def sensor_process(env, sensor):
    while True:
        data = f"Data from Sensor {sensor.device_id}"
        sensor.send_data(data)
        yield env.timeout(10)  # Sensor sends data every 10 time units

def main():
    env = simpy.Environment()

    # Generate a set of IoT devices
    devices = generate_devices(num_sensors=10, num_actuators=5, num_controllers=3)

    # Initialize network graph and add devices to it
    network = nx.Graph()
    for device in devices:
        network.add_node(device.device_id, type=device.device_type)
        # You can also add edges (connections) here based on your logic

    # Start the sensor processes
    for device in devices:
        if isinstance(device, Sensor):
            env.process(sensor_process(env, device))

    env.run(until=100)  # Run the simulation for 100 time units

if __name__ == "__main__":
    main()
