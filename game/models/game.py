from django.utils.translation import gettext as _
from django_extensions.db.models import TimeStampedModel


class Game(TimeStampedModel):
    class Meta:
        verbose_name = _("Game")
        verbose_name_plural = _("Games")

    def __str__(self):
        return f"Game started at {self.created}"
