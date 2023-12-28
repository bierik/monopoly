from statemachine import State, StateMachine

from core.game.dice import Dice


class GameMachine(StateMachine):
    idle = State("Idle", initial=True)
    turn_started = State("Turn started")
    dice_rolled = State("Dice rolled", enter="do_dice_roll")
    moving = State("Moving", enter="apply_move")
    turn_ended = State("Turn ended", enter="hand_over_turn")
    lost = State("Lost", final=True)

    start_turn = idle.to(turn_started, cond="is_players_turn") | turn_ended.to(turn_started, cond="is_players_turn")
    roll_dice = turn_started.to(dice_rolled)
    move = dice_rolled.to(moving)
    end_turn = moving.to(turn_ended)
    lose = turn_ended.to(lost)

    def __init__(self, participation):
        self.participation = participation
        self.dice = Dice()
        super().__init__()

    def is_players_turn(self):
        return self.participation.is_players_turn

    def hand_over_turn(self):
        self.participation.game.hand_over_turn()

    def do_dice_roll(self):
        self.dice.roll()

    def apply_move(self):
        self.participation.move(self.dice.sum())
