from django.db.models.signals import post_save
from django.dispatch import receiver

from core.game.models import Game, GameStatus, Participation
from core.mqtt_client import mqtt_client


@receiver(post_save, sender=Participation)
def check_participation_count(sender, instance, **kwargs):
    participation = instance
    game = participation.game
    if game.max_participations == game.participations.count():
        game.start()


@receiver(post_save, sender=Game)
def game_started(sender, instance, **kwargs):
    game = instance
    if game.status == GameStatus.RUNNING:
        mqtt_client.publish("game/started", {"game_id": game.pk})


@receiver(post_save, sender=Participation)
def game_joined(sender, instance, **kwrags):
    participation = instance
    mqtt_client.publish("game/joined", {"game_id": participation.game.pk})


@receiver(post_save, sender=Game)
def game_created(sender, instance, **kwargs):
    game = instance
    if game.status == GameStatus.CREATED:
        mqtt_client.publish("game/created", {"game_id": game.pk})
