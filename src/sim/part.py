import numpy as np


def src_rework_10():
    if np.random.rand() > 0.1:
        return Part()
    else:
        return Part(planned="NA")


def src_part(group, type=""):
    def func():
        return Part(group=group, type=type)

    return func


def src_SLT_5():
    return Part(planned=["SLT5"])


class Part:
    def __init__(self, group="", type="", seq_nr=None, planned=[]) -> None:
        self.seq_nr = seq_nr
        self.group = group
        self.type = type
        self.planned = planned
        self.passed = []

    def __eq__(self, other: object) -> bool:
        if (
            other in self.passed
            or other == self.type
            or other == self.seq_nr
            or other == self.group
        ):
            return True
        return False

    def check(self, toDo):
        if toDo in self.planned:
            self.planned.remove(toDo)
        if not toDo in self.passed:
            self.passed.append(toDo)

    def schedule(self, toDo):
        if not toDo in self.planned:
            self.planned.append(toDo)
