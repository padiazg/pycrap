def parse_int(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        return 0
    except TypeError:
        return -1


def read_and_parse(filename: str) -> int:
    try:
        with open(filename) as f:
            data = f.read()
            return int(data.strip())
    except (FileNotFoundError, ValueError):
        return 0
