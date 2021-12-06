from .part import src_simple
from .buffer import Buffer
from .templates import SimObject


def src_SLT(size):
    return lambda: SLT(size)


class SLT(Buffer):
    def __init__(self, size, name="", generator=None) -> None:
        super().__init__(name, size)
        if generator == None:
            generator = src_simple
        self.parts = [generator() for _ in range(size)]
        self.fill << size
        for key, val in self.parts[0].__dict__.items():
            if all(
                [
                    self.parts[i].__dict__[key] == self.parts[i + 1].__dict__[key]
                    for i in range(size - 1)
                ]
            ):
                self.__dict__.update({key: val})

    def dispose(self):
        self.fill << None


class LoadingStationIn(SimObject):
    def __init__(self, name):
        self.slt = None
        super().__init__(name)

    def req_give(self, **kwargs):
        if self.slt == None:
            return False
        return self.slt.req_give(**kwargs)

    def give(self, **kwargs):
        if self.slt == None:
            return False
        return self.slt.give(**kwargs)

    def req_receive(self, **kwargs):
        if self.slt == None or self.slt.fill == 0:
            return True
        return False

    def receive(self, part, **kwargs):
        if self.slt == None or self.slt.fill == 0:
            if not self.slt == None:
                self.slt.dispose()
            self.slt = part
            return True
        return False
