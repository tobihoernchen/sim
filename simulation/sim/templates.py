from .traced import String
from .core import core


mod_rework_done = lambda x, **kwargs: x.check("NA")
mod_rework_create = lambda x, **kwargs: x + "NA"
mod_inline_measure = lambda x, **kwargs: x.check("IMT")
mod_us_testing = lambda x, **kwargs: x.check("US")
mod_geo = lambda x, **kwargs: x.check("Geo")
mod_idle = lambda x, **kwargs: x

cond_rework = lambda x, **kwargs: x == "NA"
cond_inline = lambda x, **kwargs: x == "IMT"
cond_us = lambda x, **kwargs: x == "US"
cond_geo = lambda x, **kwargs: x == "Geo"
cond_all = lambda x, **kwargs: True
cond_part_present = lambda x, **kwargs: type(x) == str


class Step:
    def __init__(
        self,
        obj,
        cond=None,
        cond_args=[],
        mod=None,
        mod_args=[],
        time=None,
        timeto=None,
        **kwargs
    ):
        self.obj = obj
        self.cond = cond if cond != None else cond_all
        self.cond_args = cond_args
        self.mod = mod if mod != None else mod_idle
        self.mod_args = mod_args
        self.time = time
        self.timeto = timeto
        self.kwargs = kwargs


class Pick(Step):
    def __init__(
        self,
        obj,
        time,
        timeto=None,
        add_condition=None,
        add_condition_args=[],
        position=0,
    ):
        if add_condition != None:
            cond = lambda **x: add_condition(**x) and obj.req_give(position=position)
        else:
            cond = lambda: obj.req_give(position=position)
        return super().__init__(
            obj,
            cond=cond,
            cond_args=add_condition_args + ["part"],
            mod=lambda: {"part": obj.give(position=position)},
            time=time,
            timeto=timeto,
        )


class Place(Step):
    def __init__(
        self,
        obj,
        time,
        timeto=None,
        add_condition=None,
        add_condition_args=[],
        position=0,
    ):
        if add_condition != None:
            cond = lambda **x: add_condition(**x) and obj.req_receive(
                **x, position=position
            )
        else:
            cond = lambda **x: obj.req_receive(**x, position=position)
        return super().__init__(
            obj,
            cond=cond,
            cond_args=add_condition_args + ["part"],
            mod=lambda **x: obj.receive(**x, position=position),
            mod_args=["part"],
            time=time,
            timeto=timeto,
        )


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
