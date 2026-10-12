import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    total: int
    page: int
    per_page: int

    @property
    def last_page(self) -> int:
        return math.ceil(self.total / self.per_page)
