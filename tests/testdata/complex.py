def very_complex(x: int) -> int:
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            if x > 60:
                                if x > 70:
                                    return 8
                                return 7
                            return 6
                        return 5
                    return 4
                return 3
            return 2
        return 1
    return 0


def with_switch(x: int) -> int:
    match x:
        case 1:
            return 1
        case 2:
            return 2
        case 3:
            return 3
        case _:
            return 0


def with_loops(n: int) -> int:
    total = 0
    for i in range(n):
        total += i
    while total > 100:
        total //= 2
    return total


def with_bool_ops(a: bool, b: bool, c: bool) -> bool:
    return a and b or c
