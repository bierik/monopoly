import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    pass


def on_message(client, userdata, msg):
    pass


client = mqtt.Client()
client.on_connect = on_connect

client.connect_async("localhost", 1883, 60)
