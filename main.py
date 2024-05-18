import simpy
import random
from devices import Sensor, Actuator, Controller, MessageBroker

def sensor_process(env, sensor):
    while True:
        if random.random() < 0.1:
            sensor.disconnect()
            yield env.timeout(random.randint(5, 20))
            sensor.connect()
        else:
            data = sensor.generate_data()
            message = f"{sensor.sensor_type},{data}"
            sensor.send_message(message, "Controller")
        yield env.timeout(10)

def main():
    env = simpy.Environment()
    broker = MessageBroker()

    sensors = [Sensor(i, random.choice(['temperature', 'humidity', 'motion']), broker) for i in range(1, 11)]
    actuators = [Actuator(i, 'heater', broker) for i in range(6, 11)]
    controllers = [Controller(i, actuators, broker) for i in range(11, 13)]

    for device in sensors + actuators + controllers:
        device.connect()

    for sensor in sensors:
        env.process(sensor_process(env, sensor))

    env.run(until=100)

if __name__ == "__main__":
    main()
