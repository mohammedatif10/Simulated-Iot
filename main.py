import simpy
import random
import time
import matplotlib.pyplot as plt
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

def simulate_scenario(env, broker, sensors):
    for sensor in sensors:
        env.process(sensor_process(env, sensor))
    env.run(until=100)

def analyze_performance(broker):
    log = broker.get_message_log()
    if not log:
        print("No messages were logged.")
        return

    total_messages = len(log)
    total_data = sum(entry['message_size'] for entry in log)
    latencies = []
    for entry in log:
        send_time = entry['timestamp']
        receive_time = time.time()
        latencies.append(receive_time - send_time)

    avg_throughput = total_data / total_messages
    avg_latency = sum(latencies) / total_messages

    print(f"Total messages: {total_messages}")
    print(f"Total data: {total_data} bytes")
    print(f"Average throughput: {avg_throughput} bytes/message")
    print(f"Average latency: {avg_latency:.2f} seconds/message")

    # Plot throughput
    timestamps = [entry['timestamp'] for entry in log]
    message_sizes = [entry['message_size'] for entry in log]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, message_sizes, marker='o')
    plt.xlabel('Time')
    plt.ylabel('Message Size (bytes)')
    plt.title('Data Throughput Over Time')
    plt.grid(True)
    plt.savefig('throughput.png')
    plt.show()

    # Plot latency
    plt.figure(figsize=(10, 5))
    plt.plot(range(total_messages), latencies, marker='x')
    plt.xlabel('Message Index')
    plt.ylabel('Latency (seconds)')
    plt.title('Latency of Messages')
    plt.grid(True)
    plt.savefig('latency.png')
    plt.show()

def create_interaction_log(broker):
    log = broker.get_message_log()
    with open('interaction_log.txt', 'w', encoding='utf-8') as f:
        for entry in log:
            f.write(f"Time: {entry['timestamp']:.2f}, Sender: {entry['sender_type']} {entry['sender_id']}, Recipient: {entry['recipient_type']} {entry['recipient_id']}, Message: {entry['message']}\n")

def main():
    env = simpy.Environment()
    broker = MessageBroker()

    sensors = [Sensor(i, random.choice(['temperature', 'humidity', 'motion']), broker) for i in range(1, 6)]
    actuators = [Actuator(i, 'heater', broker) for i in range(5, 7)]
    controllers = [Controller(i, actuators, broker) for i in range(7, 9)]

    for device in sensors + actuators + controllers:
        broker.subscribe(device, device.device_type)

    simulate_scenario(env, broker, sensors)
    analyze_performance(broker)
    create_interaction_log(broker)

if __name__ == "__main__":
    main()
