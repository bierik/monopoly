import json
import random

from django.conf import settings
from paho.mqtt.client import CallbackAPIVersion
from paho.mqtt.client import Client


def _create_client_id():
    return f"python-mqtt-{random.randint(0, 1000)}"  # noqa: S311


class MQTTClient:
    def __init__(self, host=settings.MQTT_HOST, port=settings.MQTT_PORT):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        self.client = Client(client_id=_create_client_id(), callback_api_version=CallbackAPIVersion.VERSION2)
        self.client.reconnect_delay_set(min_delay=10, max_delay=10)
        self.client.connect_async(self.host, self.port)
        self.client.loop_start()

    def disconnect(self, resoncode=0):
        self.client.disconnect(resoncode)

    def publish(self, topic, payload):
        self.client.publish(topic, payload=json.dumps(payload), qos=2)

    def publish_game_created(self, game):
        self.publish(f"{game.device.token}/game/created", {"id": game.id})

    def publish_game_changed(self, game):
        self.publish(f"game/{game.pk}/changed", {"id": game.id})

    def publish_participation_created(self, participation):
        self.publish("participation/created", {"id": participation.id})

    def publish_participation_changed(self, participation):
        self.publish(f"participation/{participation.pk}/changed", {"id": participation.id})

    def publish_character_moved(self, participation):
        self.publish(
            f"game/{participation.game.pk}/moved", {"id": participation.id, "tile": participation.current_tile.identifier}
        )

    def publish_action(self, participation, action):
        self.publish(f"participation/{participation.pk}/action", {"id": participation.id, "action": action})


mqtt_client = MQTTClient()
