from .buffer import Buffer
from .part import Part

cond_SLT = lambda x, **kwargs: any(["SLT" in i for i in x.planned])


class LoadingStationIn(Buffer):
    def __init__(self, name, max_nr_parts):
        super().__init__(name, max_nr_parts)

    def req_receive(self, part, **kwargs):
        if self.fill == 0 and not self.state == "busy" and cond_SLT(part):
            return True
        return False

    def receive(self, part, **kwargs):
        if self.fill == 0 and not self.state == "busy" and cond_SLT(part):
            parts = self.mod_slt(part)
            if len(parts) <= self.max_parts:
                for part, i in zip(parts, range(len(parts))):
                    self.parts[i] = part
                    self.reserved[i] = False
            else:
                print("SLT too large!")
            self.state >> "busy"
            self.fill << len(parts)
            return True
        return False

    def mod_slt(self, x):
        size = int([s[3:] for s in x.planned if "SLT" in s][0])
        return [Part(group=x.group, type=x.type) for i in range(size)]
