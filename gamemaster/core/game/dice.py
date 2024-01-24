import random


def roll_dice():
    roll_1 = random.randint(1, 6)
    roll_2 = random.randint(1, 6)
    return (roll_1 + roll_2, roll_1 == roll_2)
