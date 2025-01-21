from dataclasses import dataclass
from datetime import date


@dataclass
class Lesson:
    num: int
    info: str
    date: date
    group_num: int
    class_letter: str = None
