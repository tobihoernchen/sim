from .templates import SimObject, Program, cond_all, mod_idle
from .part import Part
from .traced import Int


def cond_buffer_empty(buf):
    def bufferempty(**kwargs):
        return buf.fill == 0

    return bufferempty


def cond_buffer_contains(buf, contains):
    def buffercontains(**kwargs):
        return any([part == contains for part in buf.parts])

    return buffercontains


def cond_buffer_contains_not(buf, contains):
    def buffercontains(**kwargs):
        return not any([part == contains for part in buf.parts])

    return buffercontains


def cond_buffer_willing_receive(buf, part=None, position=None):
    return lambda **kwargs: buf.req_receive(
        part=part, reserving=False, position=position
    )


class Buffer(SimObject):
    def __init__(self, name, capacity):
        super().__init__(name)
        self.state.prefix = "State_"
        self.max_parts = capacity
        self.parts = [False for part in range(capacity)]
        self.reserved = [False for part in range(capacity)]
        self.fill = Int(self, postfix="_Fill")

    def get_free_spot(self, reserved=False, **kwargs):
        for i in range(len(self.parts)):
            if not self.parts[i] and self.reserved[i] == reserved:
                return i
        return False

    def get_part_to_give(self, part="", reserved=False, **kwargs):
        for i in range(len(self.parts)):
            if self.parts[i]:
                if part == self.parts[i] and self.reserved[i] == reserved:
                    return i
        return False

    def req_receive(self, part, reserving=True, **kwargs):
        if self.fill < self.max_parts and not self.state == "busy":
            spot = self.get_free_spot(part=part, **kwargs)
            if type(spot) == int:
                if reserving:
                    self.reserved[spot] = True
                    self.state << "loading_active"
                    self.fill += 1
                return True
        return False

    def receive(self, part, **kwargs):
        if not self.state == "busy":
            spot = self.get_free_spot(reserved=True, part=part, **kwargs)
            if type(spot) == int:
                self.parts[spot] = part
                self.reserved[spot] = False
                self.state >> "loading_active"
                return True
        return False

    def req_give(self, part="", reserving=True, **kwargs):
        if self.fill > 0 and not self.state == "busy":
            spot = self.get_part_to_give(part, **kwargs)
            if type(spot) == int:
                if reserving:
                    self.reserved[spot] = True
                    self.state << "unloading_active"
                return True
        return False

    def give(self, part="", **kwargs):
        if self.fill > 0 and not self.state == "busy":
            spot = self.get_part_to_give(part, reserved=True, **kwargs)
            if type(spot) == int:
                self.fill -= 1
                part = self.parts[spot]
                self.parts[spot] = False
                self.reserved[spot] = False
                self.state >> "unloading_active"
                return part
        return False

    def end(self):
        self.fill.update()
        return super().end()


class Jig(Buffer):
    def __init__(self, name):
        super().__init__(name, 1)


class BufferWorkOn(Program):
    def __init__(
        self, name, time, places=None, condition=None, modifier=None, parent=None
    ):
        """Simple program to work an a part and only release it after the work is done.

        Keyword Arguments:
        time: Time to work on the part.
        condition: Function that takes the part string and returns boolean.
        modifier: Function that takes the part string and returns a modified one.
        """
        super().__init__(name, parent)
        self.workon_time = time

        self.condition = condition
        if condition == None:
            self.condition = cond_all

        self.places = places
        if places == None:
            self.places = range(len(self.parent.parts))

        self.modifier = modifier
        if modifier == None:
            self.modifier = mod_idle

        self.code = self.code_gen()

    def code_gen(self):
        while True:
            # Teil anwesend?
            success = False
            while not success:
                for part_nr in self.places:
                    if self.parent.parts[part_nr]:
                        if self.condition(self.parent.parts[part_nr]):
                            success = True
                            break
                yield
            # Blockieren
            self.activate()
            self.parent.reserved[part_nr] = True
            self.waitfor(self.workon_time)
            yield
            modded = self.modifier(self.parent.parts[part_nr])
            self.parent.parts[part_nr] = modded
            self.parent.reserved[part_nr] = False
            self.deactivate()
            self.trigger_update()
            yield


class BufferSource(Program):
    def __init__(
        self,
        name,
        respawn_time,
        transfer_time,
        parent=None,
        position=0,
        getNextPart=None,
    ):
        super().__init__(name, parent)
        self.respawn_time = respawn_time
        self.transfer_time = transfer_time
        self.code = self.code_gen()
        self.getNextPart = getNextPart
        self.position = position

    def code_gen(self):
        while True:
            while True:
                if self.getNextPart == None:
                    next_part = Part()
                else:
                    next_part = self.getNextPart()
                if not self.parent.req_receive(part=next_part, position=self.position):
                    yield
                else:
                    break
            # Blockieren
            self.waitfor(self.transfer_time)
            yield
            self.activate()
            self.parent.receive(part=next_part, position=self.position)
            self.deactivate()
            self.trigger_update()
            self.waitfor(self.respawn_time)
            yield

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True


class BufferDrain(Program):
    def __init__(self, name, time, parent=None, position=0):
        super().__init__(name, parent)
        self.remove_time = time
        self.code = self.code_gen()
        self.part = None
        self.position = position
        self.first_drain = -1
        self.nr_drains = 0
        self.jph = Int(self.parent, "JPH-")

    def doc(self):
        self.nr_drains += 1
        if self.first_drain == -1:
            self.first_drain = self.parent.core.now
        if self.parent.core.now != self.first_drain:
            self.jph << int(
                self.nr_drains * 3600 / (self.parent.core.now - self.first_drain)
            )

    def code_gen(self):
        while True:
            # Warten
            self.activate()
            self.waitfor(self.remove_time)
            yield
            # Teil anfordern
            while not self.parent.req_give(position=self.position):
                yield
            self.part = self.parent.give(position=self.position)
            self.doc()
            self.deactivate()
            self.trigger_update()
            yield

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True
