VERSION = "0.1.0"


class VersionInfo:
    def __init__(self) -> None:
        self.version = VERSION
        self.major, self.minor, self.patch = self._parse(VERSION)

    @staticmethod
    def _parse(v: str) -> tuple[int, int, int]:
        parts = v.lstrip("v").split(".")
        parts += ["0"] * (3 - len(parts))
        try:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return (0, 0, 0)

    def __str__(self) -> str:
        return self.version


SPLASH = """
┏┓  ┏┓        Version: {v.major}.{v.minor}.{v.patch}
┃┓┏┓┃ ┏┓┏┓┏┓  Tool: py-crap
┗┛┗┛┗┛┛ ┗┻┣┛  CRAP score calculator for Python
          ┛
"""


def splash() -> str:
    return SPLASH.strip().format(v=VersionInfo())
