import json
import random

from paho.mqtt.client import Client


def _create_client_id() -> str:
    return f"python-mqtt-{random.randint(0, 1000)}"


class MQTTClient:
    def __init__(self, host="mosquitto", port=1883):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        self.client = Client(_create_client_id())
        self.client.connect_async(self.host, self.port)
        self.client.loop_start()

    def disconnect(self, resoncode=0):
        self.client.disconnect(resoncode)

    def publish(self, topic, payload):
        self.client.publish(topic, payload=json.dumps(payload), qos=2)


mqtt_client = MQTTClient()
