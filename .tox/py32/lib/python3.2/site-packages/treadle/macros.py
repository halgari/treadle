from .treadle import *


def And(expr, *rest):
    if rest:
        return If(expr, And(*rest), ConstFalse)
    else:
        return If(expr, ConstTrue, ConstFalse)
