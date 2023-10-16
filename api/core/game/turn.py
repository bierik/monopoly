class Turn:
    def __init__(self):
        pass

    def run(self, participation):
        raise NotImplementedError()


class MoveForward(Turn):
    def __init__(self, steps):
        self.steps = steps

    def run(self, participation):
        pass
