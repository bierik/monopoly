from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from core.board import monopoly_swiss
from core.device.models import Device
from core.game.models import Character, Game, GameStatus, Participation

User = get_user_model()

fixtures = Path(__file__).parent / "fixtures"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--participations", type=int, default=4)

    def handle(self, *args, participations, **options):
        board = monopoly_swiss.create()
        admin, _ = User.objects.get_or_create(username="admin", is_superuser=True, is_staff=True)
        admin.set_password("admin")
        admin.save()

        lisa, _ = User.objects.get_or_create(username="lisa")
        lisa.set_password("admin")
        lisa.save()
        leon, _ = User.objects.get_or_create(username="leon")
        leon.set_password("admin")
        leon.save()
        franz, _ = User.objects.get_or_create(username="franz")
        franz.set_password("admin")
        franz.save()
        peter, _ = User.objects.get_or_create(username="peter")
        peter.set_password("admin")
        peter.save()

        players = [lisa, leon, franz, peter]

        with (fixtures / "Cat.gltf").open() as f:
            cat, _ = Character.objects.get_or_create(
                identifier="cat", defaults={"name": "Cat", "model": File(f, name="cat.gltf")}
            )
        with (fixtures / "Wolf.gltf").open() as f:
            wolf, _ = Character.objects.get_or_create(
                identifier="wolf", defaults={"name": "Wolf", "model": File(f, name="wolf.gltf")}
            )
        with (fixtures / "Dog.gltf").open() as f:
            dog, _ = Character.objects.get_or_create(
                identifier="dog", defaults={"name": "Dog", "model": File(f, name="dog.gltf")}
            )
        with (fixtures / "Pig.gltf").open() as f:
            pig, _ = Character.objects.get_or_create(
                identifier="pig", defaults={"name": "Pig", "model": File(f, name="pig.gltf")}
            )

        characters = [cat, wolf, dog, pig]

        device, _ = Device.objects.get_or_create(token=uuid4())
        game, _ = Game.objects.get_or_create(owner=lisa, board=board, device=device, max_participations=participations)

        for player, character in zip(players[:participations], characters[:participations]):
            if not Participation.objects.filter(game=game, player=player).exists():
                game.join(player, character)

        if game.status != GameStatus.RUNNING:
            game.start()
