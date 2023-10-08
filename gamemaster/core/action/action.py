class Action:
    title = ""
    text = ""
    triggers = []

    def __call__(self, participation, trigger):
        if trigger is None or trigger in self.triggers:
            self.run(participation=participation)

    def run(self, participation):
        pass


class NoopAction(Action):
    pass
