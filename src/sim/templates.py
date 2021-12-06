from .traced import String
from .core import core


def mod_rework_done(x, **kwargs):
    x.check("NA")
    return x


def mod_rework_create(x, **kwargs):
    x + "NA"
    return x


def mod_inline_measure(x, **kwargs):
    x.check("IMT")
    return x


def mod_us_testing(x, **kwargs):
    x.check("US")
    return x


mod_idle = lambda x, **kwargs: x

cond_rework = lambda x, **kwargs: x == "NA"
cond_inline = lambda x, **kwargs: x == "IMT"
cond_us = lambda x, **kwargs: x == "US"
cond_all = lambda x, **kwargs: True
cond_part_present = lambda x, **kwargs: type(x) == str


def cond_part(cond):
    return lambda x, **kwargs: x == cond


def mod_part(cond):
    return lambda x, **kwargs: x.check(cond)


class SimObject:
    def __init__(self, name):
        self.name = name
        self.core = None
        self.programs = []
        core.addObject(self)
        self.state = String(self, "State_")

    def add_program(self, program):
        program.parent = self
        self.programs.append(program)

    def wake(self):
        for prog in self.programs:
            next(prog.run)

    def end(self):
        self.state.update()
        for prog in self.programs:
            prog.end()

    def trigger_update(self):
        self.core.scheduler.append(self.core.now)


class Program:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        if parent is not None:
            parent.add_program(self)

        self.waitingfor = 0
        self.active = False
        self.code = self.code_gen()
        self.run = self.run_gen()

    def trigger_update(self):
        self.parent.core.scheduler.append(self.parent.core.now)

    def waitfor(self, offset):
        self.parent.core.scheduler.append(self.parent.core.now)
        self.parent.core.scheduler.append(self.parent.core.now + offset)
        self.waitingfor = self.parent.core.now + offset
        return

    def run_gen(self):
        while True:
            while self.parent.core.now < self.waitingfor:
                yield
            next(self.code)
            yield

    def code_gen(self):
        while True:
            yield

    def end(self):
        if self.active:
            self.deactivate()

    def deactivate(self):
        self.active = False
        self.parent.state >> self.name
        self.parent.state >> "busy"

    def activate(self):
        self.parent.state << self.name
        self.parent.state << "busy"
        self.active = True
