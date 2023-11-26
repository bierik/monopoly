import random

from paho.mqtt.client import Client


def _create_client_id() -> str:
    return f"python-mqtt-{random.randint(0, 1000)}"


class MQTTClient:
    def __init__(self, host: str = "mosquitto", port: int = 1883):
        self.host: str = host
        self.port: int = port
        self.client: Client = None

    def connect(self):
        self.client = Client(_create_client_id())
        self.client.connect(self.host, self.port)

    def disconnect(self, resoncode: int = 0) -> None:
        self.client.disconnect(resoncode)

    def publish(self, topic: str, payload) -> None:
        self.client.publish(topic, payload)


client = MQTTClient()
