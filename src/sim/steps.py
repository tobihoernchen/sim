from .templates import cond_all, mod_idle


class Step:
    def __init__(
        self,
        cond=None,
        cond_args=[],
        mod=None,
        mod_args=[],
        time=None,
        timeto=None,
        blocking=None,
        **kwargs
    ):
        self.cond = cond if cond != None else cond_all
        self.cond_args = cond_args
        self.mod = mod if mod != None else mod_idle
        self.mod_args = mod_args
        self.time = time
        self.timeto = timeto
        self.kwargs = kwargs
        self.blocking = blocking


class Pick(Step):
    def __init__(
        self,
        obj,
        time,
        timeto=None,
        certain_part=None,
        start_condition=None,
        start_condition_args=[],
        blocking=None,
        position=0,
    ):
        if start_condition != None:
            if certain_part == None:
                cond = lambda **x: start_condition(**x) and obj.req_give(
                    position=position
                )
            else:
                cond = lambda **x: start_condition(**x) and obj.req_give(
                    part=certain_part, position=position
                )
        else:
            if certain_part == None:
                cond = lambda **x: obj.req_give(position=position)
            else:
                cond = lambda **x: obj.req_give(part=certain_part, position=position)

        if certain_part == None:
            mod = lambda **x: {"part": obj.give(position=position)}
        else:
            mod = lambda **x: {"part": obj.give(part=certain_part, position=position)}

        return super().__init__(
            cond=cond,
            cond_args=start_condition_args + ["part"],
            mod=mod,
            time=time,
            timeto=timeto,
            blocking=blocking,
        )


class Place(Step):
    def __init__(
        self,
        obj,
        time,
        timeto=None,
        start_condition=None,
        start_condition_args=[],
        blocking=None,
        position=0,
    ):
        if start_condition != None:
            cond = lambda **x: start_condition(**x) and obj.req_receive(
                **x, position=position
            )
        else:
            cond = lambda **x: obj.req_receive(**x, position=position)
        return super().__init__(
            cond=cond,
            cond_args=start_condition_args + ["part"],
            mod=lambda **x: obj.receive(**x, position=position),
            mod_args=["part"],
            time=time,
            timeto=timeto,
            blocking=blocking,
        )


class Wait(Step):
    def __init__(self, time=None, timeto=None, blocking=None, **kwargs):
        return super().__init__(time=time, timeto=timeto, blocking=blocking ** kwargs)


class WaitForCond(Step):
    def __init__(
        self, cond=None, cond_args=[], time=None, timeto=None, blocking=None, **kwargs
    ):
        return super().__init__(
            cond=cond,
            cond_args=cond_args,
            time=time,
            timeto=timeto,
            blocking=blocking,
            **kwargs
        )
