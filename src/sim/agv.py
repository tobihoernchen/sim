from .templates import SimObject, Program
from .traced import String


def cond_agv_isFree(pos):
    def cond_isFree(prg, **kwargs):
        return prg.parent.course.isFree(pos)

    return cond_isFree


class AgvCourse:
    def __init__(self, positions=[], distances_time=[]):
        self.agvs = []
        self.positions = positions
        self.distances = distances_time

    def register(self, agv, position):
        if type(agv) == list:
            for ag, pos in zip(agv, position):
                self.registerSingle(ag, pos)
        else:
            self.registerSingle(agv, position)

    def registerSingle(self, agv, pos):
        self.agvs.append(agv)
        agv.position << pos
        agv.course = self

    def isFree(self, pos):
        return not any([agv.position == pos for agv in self.agvs])


class AGV(SimObject):
    def __init__(self, name, course, position):
        super().__init__(name)
        self.position = String(self, "Pos_")
        self.last_change = 0
        course.register(self, position)

    def end(self):
        self.position.update()
        return super().end()


class AgvStep:
    def __init__(self, pos, waitfor=None, step=None):
        self.pos = pos
        self.waitfor = waitfor
        self.step = step


class AgvDrive(Program):
    def __init__(
        self,
        name,
        steps=[],
        parent=None,
    ):
        self.positions_cond = positions_cond
        self.conditions = conditions
        self.positions_take = positions_take
        self.take_from = take_from
        self.positions_place = positions_place
        self.place_at = place_at
        super().__init__(name, parent=parent)

    def code_gen(self):
        load = ""
        while True:
            actual_pos = self.parent.position
            if actual_pos in self.positions_take:
                take_i = self.positions_take.index(actual_pos)
                while not self.take_from[take_i].req_give():
                    yield
                load = self.take_from[take_i].give()
                self.trigger_update()
            if actual_pos in self.positions_place and not isinstance(load, str):
                place_i = self.positions_place.index(actual_pos)
                while not self.place_at[place_i].req_receive(load):
                    yield
                self.place_at[place_i].receive(load)
                self.trigger_update()
                load = ""
            if actual_pos in self.positions_cond:
                check_i = self.positions_cond.index(actual_pos)
                while not self.conditions[check_i](prg=self):
                    yield

            actual_pos_i = self.parent.course.positions.index(actual_pos)
            next_pos_i = actual_pos_i + 1
            if next_pos_i == len(self.parent.course.positions):
                next_pos_i = 0
            next_pos = self.parent.course.positions[next_pos_i]
            distance = self.parent.course.distances[actual_pos_i]
            self.parent.position << ""
            self.parent.position << "driving-" + next_pos
            self.waitfor(distance)
            yield
            self.parent.position << ""
            self.parent.position << next_pos
