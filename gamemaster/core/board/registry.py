class UnknownBoardException(Exception):
    def __init__(self, identifier):
        super().__init__(f"Structure with identifier {identifier} not found")


class BoardRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, board, identifier):
        if identifier in self.registry:
            return
        self.registry[identifier] = board

    def board_for_identifier(self, identifier):
        if identifier not in self.registry:
            raise UnknownBoardException(identifier)
        return self.registry[identifier]


board_registry = BoardRegistry()
