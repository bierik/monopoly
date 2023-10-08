from statemachine import StateMachine


class PersistListener:
    def after_transition(self, model, machine, **kwargs):
        model.save(update_fields=[machine.state_field])


class PersistentStateMachine(StateMachine):
    def __init__(self, *args, listeners=None, **kwargs):
        listeners = listeners or []
        super().__init__(*args, **kwargs, listeners=[*listeners, PersistListener()])
