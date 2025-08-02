import math


def roundu(num: float) -> int:
    shot, intgr = math.modf(num)
    intgr = int(intgr)

    return intgr + 1 if shot >= 0.5 else intgr
