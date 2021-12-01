from .templates import SimObject, Program, Step, cond_all


class Rob(SimObject):
    def __init__(self, name):
        super().__init__(name)
        self.state.prefix = "Program_"

    def wake(self):
        for prog in self.programs:
            if self.state == "busy" and prog.active or not self.state == "busy":
                next(prog.run)


class RobHandling(Program):
    def __init__(
        self,
        name,
        take_from,
        place_at,
        pick_dur,
        transport_dur,
        place_dur,
        parent=None,
        take_from_position=0,
        place_at_position=0,
    ):
        """Simple program for handling parts from one object to another"""

        super().__init__(name, parent=parent)

        self.take_from, self.take_from_position = take_from, take_from_position
        self.place_at, self.place_at_position = place_at, place_at_position

        self.pick_dur = pick_dur
        self.place_dur = place_dur
        self.transport_dur = transport_dur

        self.code = self.code_gen()

    def code_gen(self):
        while True:
            while not self.take_from.req_give(position=self.take_from_position):
                yield
            self.activate()
            self.waitfor(self.pick_dur)
            yield
            part = self.take_from.give(position=self.take_from_position)
            self.waitfor(self.transport_dur)
            yield
            while not self.place_at.req_receive(part, position=self.place_at_position):
                yield
            self.waitfor(self.place_dur)
            yield
            self.place_at.receive(part, position=self.place_at_position)
            self.deactivate()
            self.trigger_update()
            yield


class RobHandlingConditional(Program):
    def __init__(
        self,
        name,
        take_from,
        places_at,
        conditions,
        pick_dur,
        transport_durs,
        place_durs,
        take_from_position=0,
        places_at_position=None,
        parent=None,
    ):
        """Program that picks from one place and puts to a place depending on the picked part.

        Keyword arguments:
        take_from: Object to take from
        places_at: List of Objects to place. Last Object is default.
        transport_durs, place_durs: List with len of places_at. Describes handling time
        conditions: List of strings wit len of places_at - 1. If part contains the string, it is handled to the corresponding place.
        """
        super().__init__(name, parent=parent)
        self.take_from, self.take_from_position = take_from, take_from_position
        self.places_at = places_at
        if places_at_position == None:
            self.places_at_position = [0 for x in places_at]
        else:
            self.places_at_position = places_at_position
        self.conditions = conditions + [cond_all]

        self.pick_dur = pick_dur
        self.place_durs = place_durs
        self.transport_durs = transport_durs

        self.code = self.code_gen()

    def code_gen(self):
        while True:
            while not self.take_from.req_give(position=self.take_from_position):
                yield
            self.activate()
            self.waitfor(self.pick_dur)
            yield
            part = self.take_from.give(position=self.take_from_position)
            targets = []
            for target, condition in enumerate(self.conditions):
                if condition(part):
                    targets.append(target)
            self.waitfor(self.transport_durs[target])
            yield
            target = -1
            while target == -1:
                for potentialTarget in targets:
                    if self.places_at[potentialTarget].req_receive(
                        part, position=self.places_at_position[potentialTarget]
                    ):
                        target = int(potentialTarget)
                        break
                yield
            self.waitfor(self.place_durs[target])
            yield
            self.places_at[target].receive(
                part, position=self.places_at_position[target]
            )
            self.deactivate()
            self.trigger_update()
            yield


class RobHandlingBetter(Program):
    def __init__(
        self,
        name,
        steps,
        parent=None,
    ):
        """Program that picks from one place and puts to a place depending on the picked part.

        Keyword arguments:
        take_from: Object to take from
        places_at: List of Objects to place. Last Object is default.
        transport_durs, place_durs: List with len of places_at. Describes handling time
        conditions: List of strings wit len of places_at - 1. If part contains the string, it is handled to the corresponding place.
        """
        super().__init__(name, parent=parent)
        self.part = None
        self.steps = steps
        self.code = self.code_gen()

    def code_gen(self):
        while True:
            for step in self.steps:
                if isinstance(step, list):
                    while not res:
                        for substep in step:
                            if isinstance(substep, Step):
                                cond_args = dict(
                                    (k, self.__dict__[k]) for k in substep.cond_args
                                )
                                res = substep.cond(cond_args)
                                if res:
                                    break

                            while not step.cond(**cond_args):
                                yield
                            if not self.active:
                                self.activate()
                    if not self.active:
                        self.activate()
                    if substep.time != None:
                        self.waitfor(step.time)
                        yield
                    mod_args = dict((k, self.__dict__[k]) for k in substep.mod_args)
                    if isinstance(res, dict):
                        res = substep.mod(**mod_args)
                        for k, val in res.items():
                            self.__dict__[k] = val
                        self.trigger_update()

                elif isinstance(step, Step):
                    if step.timeto != None:
                        self.waitfor(step.timeto)
                        yield
                    cond_args = dict((k, self.__dict__[k]) for k in step.cond_args)
                    while not step.cond(**cond_args):
                        yield
                    if not self.active:
                        self.activate()
                    if step.time != None:
                        self.waitfor(step.time)
                        yield
                    mod_args = dict((k, self.__dict__[k]) for k in step.mod_args)
                    res = step.mod(**mod_args)
                    if isinstance(res, dict):
                        for k, val in res.items():
                            self.__dict__[k] = val
                        self.trigger_update()
            self.deactivate()
            self.trigger_update()
