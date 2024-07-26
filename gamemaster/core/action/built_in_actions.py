from core.action.action import Action
from core.action.registry import register
from core.action.trigger import Triggers


@register()
class StartAction(Action):
    title = "Gehe über Start"
    description = "Du erhälst Geld"
    triggers = [Triggers.TRAVERSED]

    def run(self, participation):
        participation.balance += 200
        participation.save(update_fields=["balance"])
