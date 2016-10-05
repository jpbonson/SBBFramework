from ..default_point import DefaultPoint

class ClassificationPoint(DefaultPoint):
    """
    Encapsulates a dataset value as a point.
    """

    def __init__(self, inputs, output):
        super(ClassificationPoint, self).__init__()
        self.inputs = inputs
        self.output = output