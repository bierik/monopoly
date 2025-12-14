from enum import Enum

from statemachine import State

from app.statemachine import PersistentStateMachine


class ParticipationStates(Enum):
    IDLE = "idle"
    MOVED = "moved"


class ParticipationStateMachine(PersistentStateMachine):
    idle = State(ParticipationStates.IDLE.value, initial=True)
    moved = State(ParticipationStates.MOVED.value)

    move = idle.to(moved, cond="is_players_turn")
    end_turn = moved.to(idle, cond="is_players_turn")
