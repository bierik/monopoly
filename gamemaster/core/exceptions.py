from rest_framework.exceptions import ValidationError


class AlreadyParticipantError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Player is already participating",
            code="player_already_participating",
        )


class JoinStartedGameError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Game has already started",
            code="game_has_already_started",
        )


class SameCharacterError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="The characters have to be unique per game",
            code="unique_character",
        )


class MaxParticipationsError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="The maximum amount of participations is exceeded.",
            code="max_participations_exeeded",
        )


class LobbyNotReadyError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Not all participants have joined yet.",
            code="lobby_not_ready",
        )


class GameStartError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Game is in the wrong status to start.",
            code="game_start",
        )


class NotPlayersTurnError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="It is not the players turn.",
            code="not_players_turn",
        )


class RollDiceNotAllowedError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Player can not roll dice.",
            code="roll_dice_not_allowed",
        )


class ParticipationBlockedError(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Participation is blocked.",
            code="blocked_participation",
        )
