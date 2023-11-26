import random


class DiceNotRolledException(Exception):
    def __init__(self):
        super().__init__("Die has not yet been rolled")


class Dice:
    def __init__(self):
        self.roll_1 = None
        self.roll_2 = None
        self.is_double = False
        self.rolled = False

    def roll(self):
        self.roll_1 = random.randint(1, 6)
        self.roll_2 = random.randint(1, 6)
        self.rolled = True

    def sum(self):
        if not self.rolled:
            raise DiceNotRolledException()
        return self.roll_1 + self.roll_2
