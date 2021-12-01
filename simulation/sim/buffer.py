from .templates import SimObject, Program, cond_all, mod_idle
from .part import Part
from .traced import Int


def cond_buffer_empty(buf):
    def bufferempty(prg=None):
        return buf.fill == 0

    return bufferempty


class Buffer(SimObject):
    def __init__(self, name, capacity):
        super().__init__(name)
        self.state.prefix = "Rotation_"
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

    def req_receive(self, part, **kwargs):
        if self.fill < self.max_parts and not self.state == "busy":
            spot = self.get_free_spot(part=part, **kwargs)
            if type(spot) == int:
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

    def req_give(self, part="", **kwargs):
        if self.fill > 0 and not self.state == "busy":
            spot = self.get_part_to_give(part, **kwargs)
            if type(spot) == int:
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
    def __init__(self, name, time, condition=None, modifier=None, parent=None):
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

        self.modifier = modifier
        if modifier == None:
            self.modifier = mod_idle

        self.code = self.code_gen()

    def code_gen(self):
        while True:
            # Teil anwesend?
            success = False
            while not success:
                for part_nr in range(len(self.parent.parts)):
                    if self.parent.parts[part_nr]:
                        if self.condition(self.parent.parts[part_nr]):
                            success = True
                            break
                yield
            # Blockieren
            self.activate()
            self.parent.reserved[part_nr] = True
            yield [self.parent.core.now + self.workon_time]
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
                if not self.parent.req_receive(next_part, position=self.position):
                    yield
                else:
                    break
            # Blockieren
            self.waitfor(self.transfer_time)
            yield
            self.activate()
            self.parent.receive(next_part, position=self.position)
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

    def code_gen(self):
        while True:
            # Warten
            self.activate()
            self.waitfor(self.remove_time)
            yield
            # Teil anfordern
            while not self.parent.req_give(position=self.position):
                yield
            yield
            self.part = self.parent.give(position=self.position)
            self.deactivate()
            self.trigger_update()
            yield

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True
