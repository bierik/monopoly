from core.action.action import Action
from core.action.registry import register
from core.action.trigger import Triggers


@register()
class StartAction(Action):
    title = "Gehe über Start"
    description = "Du erhälst Geld"
    triggers = [Triggers.TRAVERSED]

    def run(self, participation, tile, context=None):
        super().run(participation, tile, context)
        participation.balance += 200
        participation.save(update_fields=["balance"])


@register()
class PunishAction(Action):
    title = "Gehe über Start"
    description = "Du erhälst Geld"
    triggers = [Triggers.LANDED_ON]

    def run(self, participation, tile, context=None):
        super().run(participation, tile, context)
        context = context or {}
        punishment = context.get("punishment", 200)
        participation.balance -= punishment
        participation.save(update_fields=["balance"])


@register()
class JailAction(Action):
    title = "Gehe ins Gefängnis"
    description = "Du must auf direktem Weg ins Gefängnis"
    triggers = [Triggers.LANDED_ON]

    def run(self, participation, tile, context=None):
        super().run(participation, tile, context)
        participation.block()
