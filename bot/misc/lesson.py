from dataclasses import dataclass
from datetime import date


@dataclass
class Lesson:
    """
    Датакласс для промежуточного хранения уроков из расписания, перед внесением в бд
    """
    num: int
    info: str
    date: date
    group_num: int
    class_letter: str = None
