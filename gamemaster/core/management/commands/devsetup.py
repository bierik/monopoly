from django.core.management.base import BaseCommand
from core.board import monopoly_swiss
from django.contrib.auth import get_user_model
from pathlib import Path
from django.core.files import File

from core.game.models import Character

User = get_user_model()

fixtures = Path(__file__).parent / 'fixtures'


class Command(BaseCommand):
    def handle(self, *args, **options):
        monopoly_swiss.create()
        admin, _ = User.objects.get_or_create(username = "admin", is_superuser=True, is_staff=True)
        admin.set_password('admin')
        admin.save()

        lisa, _ = User.objects.get_or_create(username = "lisa")
        lisa.set_password('admin')
        lisa.save()
        leon, _ = User.objects.get_or_create(username = "leon")
        leon.set_password('admin')
        leon.save()
        franz, _ = User.objects.get_or_create(username = "franz")
        franz.set_password('admin')
        franz.save()
        peter, _ = User.objects.get_or_create(username = "peter")
        peter.set_password('admin')
        peter.save()

        with (fixtures / 'Cat.gltf').open() as f:
            Character.objects.get_or_create(identifier="cat", defaults={"name": "Cat", "model": File(f, name="cat.gltf")})
        with (fixtures / 'Wolf.gltf').open() as f:
            Character.objects.get_or_create(identifier="wolf", defaults={"name": "Wolf", "model": File(f, name="wolf.gltf")})
        with (fixtures / 'Dog.gltf').open() as f:
            Character.objects.get_or_create(identifier="dog", defaults={"name": "Dog", "model": File(f, name="dog.gltf")})
        with (fixtures / 'Pig.gltf').open() as f:
            Character.objects.get_or_create(identifier="pig", defaults={"name": "Pig", "model": File(f, name='pig.gltf')})
