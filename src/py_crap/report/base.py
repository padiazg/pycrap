from abc import ABC, abstractmethod
from typing import IO

from py_crap.scan.entries import Entries


class FormatOptions:
    def __init__(
        self,
        writer: IO[str],
        base_dir: str = "",
        threshold: float = 30.0,
        detailed: bool = False,
    ) -> None:
        self.writer = writer
        self.base_dir = base_dir
        self.threshold = threshold
        self.detailed = detailed


class Formatter(ABC):
    @abstractmethod
    def format(self, entries: Entries, opts: FormatOptions) -> None: ...
