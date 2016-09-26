from ..default_opponent import DefaultOpponent

class DummyOpponent(DefaultOpponent):
    OPPONENT_ID = "dummy"

    def __init__(self, classtype, opponent_id):
        self._type = classtype
        DummyOpponent.OPPONENT_ID = opponent_id
        super(DummyOpponent, self).__init__(DummyOpponent.OPPONENT_ID)

    def initialize(self, seed):
        pass

    def execute(self, point_id_, inputs, valid_actions, is_training):
        return 0

def opponent_factory(name, opponent_id, BaseClass=DummyOpponent):
    def _custom_init(self):
        BaseClass.__init__(self, name, opponent_id)
    new_class = type(name, (BaseClass,),{"__init__": _custom_init})
    new_class.OPPONENT_ID = opponent_id
    return new_class