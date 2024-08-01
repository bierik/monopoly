from rest_framework import serializers

from core.mqtt_client import mqtt_client


class Action:
    title = ""
    text = ""
    triggers = []

    def __call__(self, participation, trigger, tile=None):
        if trigger is None or trigger in self.triggers:
            context = getattr(tile, "action_context", {})
            self.run(participation=participation, tile=tile, context=context)
            mqtt_client.publish_action(participation, self.serialize(context))

    def run(self, participation, tile, context=None):
        pass

    def serialize(self, context=None):
        context = context or {}
        title = context.get("title", self.title)
        text = context.get("text", self.text)
        return {"title": title, "text": text}


class NoopAction(Action):
    pass


class ActionContextSerializer(serializers.Serializer):
    punishment = serializers.IntegerField(min_value=0, required=False)
    title = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
