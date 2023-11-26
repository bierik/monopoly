import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceManager(models.Manager):
    def for_token(self, token):
        return self.get_queryset().get(token=token)


class Device(models.Model):
    class Meta:
        verbose_name = _("Gerät")
        verbose_name_plural = _("Geräte")

    objects = DeviceManager()

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_agent = models.TextField()

    @staticmethod
    def register(user_agent):
        return Device.objects.create(user_agent=user_agent)
