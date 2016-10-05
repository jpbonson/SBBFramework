import abc

def reset_points_ids():
    global next_point_id
    next_point_id = 0

def get_point_id():
    global next_point_id
    next_point_id += 1
    return next_point_id

class DefaultPoint(object):
    """
    Encapsulates a value from the environment as a point.
    """
    __metaclass__  = abc.ABCMeta

    def __init__(self):
        self.point_id_ = get_point_id()
        self.age_ = 0

    def __repr__(self): 
        return "("+str(self.point_id_)+")"

    def __str__(self): 
        return "("+str(self.point_id_)+")"