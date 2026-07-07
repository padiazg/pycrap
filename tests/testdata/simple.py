def simple() -> int:
    return 42


def with_if(x: int) -> int:
    if x > 0:
        return 1
    return 0


def complex_func(x: int) -> int:
    if x > 0:
        if x > 10:
            if x > 100:
                return 3
            return 2
        return 1
    return 0
