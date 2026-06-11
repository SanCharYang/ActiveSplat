from activesplat.msg import Frame
from activesplat.srv import \
    GetTopdownConfig, \
        GetTopdown, \
            SetPlannerState, \
                GetDatasetConfig, \
                    ResetEnv, \
                        SetMapper, \
                            GetOpacity, \
                                GetVoronoiGraph, \
                                    GetNavPath

TURN = 0.2
SPEED = 0.2
USE_RANDOM_SELECTION = False
USE_ROTATION_SELECTION = True
USE_HIGH_CONNECTIVITY = True
USE_HIERARCHICAL_PLAN = True