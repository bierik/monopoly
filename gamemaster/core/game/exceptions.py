from rest_framework.exceptions import ValidationError


class AlreadyParticipantException(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Player is already participating",
            code="player_already_participating",
        )


class JoinStartedGameException(ValidationError):
    def __init__(self):
        super().__init__(
            detail="Game has already started",
            code="game_has_already_started",
        )


class SameCharacterException(ValidationError):
    def __init__(self):
        super().__init__(
            detail="The characters have to be unique per game",
            code="unique_character",
        )


class MaxParticipationsExceeded(ValidationError):
    def __init__(self):
        super().__init__(
            detail="The maximum amount of participations is exceeded.",
            code="max_participations_exeeded",
        )
