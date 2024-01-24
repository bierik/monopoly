from statemachine import State, StateMachine

from core.game.dice import roll_dice


class GameMachine(StateMachine):
    idle = State("Idle", initial=True)
    turn_started = State("Turn started")
    moved = State("Moving", enter="roll_dice")
    turn_ended = State("Turn ended", enter="hand_over_turn")

    start_turn = idle.to(turn_started, cond="is_players_turn") | turn_ended.to(turn_started, cond="is_players_turn")
    move = turn_started.to(moved)
    end_turn = moved.to(turn_ended)

    def hand_over_turn(self):
        self.model.game.hand_over_turn()

    def roll_dice(self):
        res, _ = roll_dice()
        self.model.move(res)
