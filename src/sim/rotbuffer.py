from .templates import Program
from .buffer import Buffer
from .traced import Int


class RotBuffer(Buffer):
    def __init__(self, name, height, departments, rotation_time):
        super().__init__(name, height * departments)
        self.height = height
        self.departments = departments
        self.position = Int(self, postfix="_Position")
        self.desired_position = 0
        self.add_program(RotBufferRotate(name + "_rot", rotation_time))

    def available(self, position):
        first_part = position * self.height
        last_part = first_part + self.height

        return self.parts[first_part:last_part], self.reserved[first_part:last_part]

    def next_position(self, contains, position):
        offsets = [
            int((0.5 * n + 0.5) * pow(-1, n + 1)) for n in range(self.departments)
        ]
        for offset in offsets:
            realtive_position = -(self.position - position - offset) % self.departments
            parts, reserved = self.available(realtive_position)
            if type(contains) == str:
                for i in range(len(parts)):
                    if parts[i]:
                        if contains == parts[i] and reserved[i] == False:
                            return realtive_position
            else:
                for i in range(len(parts)):
                    if parts[i] == contains and reserved[i] == False:
                        return realtive_position
        return False

    def get_free_spot(self, reserved=False, **kwargs):
        if "position" in kwargs.keys():
            position = kwargs["position"]
        else:
            position = 0
        parts, reserved_parts = self.available(
            -(self.position - position) % self.departments
        )
        for i in range(len(parts)):
            if not parts[i] and reserved_parts[i] == reserved:
                return i - (self.position - position) % self.departments * self.height
        desire = self.next_position(False, position)
        if type(desire) == int:
            position_possible = (position - desire) % self.departments
            if self.position == self.desired_position:
                self.desired_position = position_possible
                self.core.scheduler.append(self.core.now)
        return False

    def get_part_to_give(self, part="", reserved=False, **kwargs):
        if "position" in kwargs.keys():
            position = kwargs["position"]
        else:
            position = 0
        parts, reserved_parts = self.available(
            -(self.position - position) % self.departments
        )
        for i in range(len(parts)):
            if parts[i] and reserved_parts[i] == reserved:
                if part == parts[i]:
                    return (
                        i - (self.position - position) % self.departments * self.height
                    )
        desire = self.next_position(part, position)
        if type(desire) == int:
            position_possible = (position - desire) % self.departments
            if self.position == self.desired_position:
                self.desired_position = position_possible
                self.core.scheduler.append(self.core.now)
        return False

    def turn(self, position):
        self.position << position


class RotBufferRotate(Program):
    def __init__(self, name, time, parent=None):
        super().__init__(name, parent)
        self.turn_time = time
        self.code = self.code_gen()

    def code_gen(self):
        while True:
            while (
                self.parent.position == self.parent.desired_position
                or self.parent.state == "loading_active"
                or self.parent.state == "unloading_active"
                or self.parent.core.now == self.parent.position.lastChange
            ):
                yield
            self.activate()
            self.parent.position << None
            self.waitfor(
                self.turn_time
                * abs(self.parent.position - self.parent.desired_position)
            )
            yield
            self.parent.turn(self.parent.desired_position)
            self.deactivate()
            self.trigger_update()
            yield
