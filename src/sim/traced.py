from .core import core


class Int:
    def __init__(self, parent, prefix="", postfix=""):
        self.history = []
        self.val = 0
        self.parent = parent
        self.lastChange = self.parent.core.now
        self.prefix = prefix
        self.postfix = postfix
        self.parent.core.addTrace(self)
        self.kill = False

    def getName(self):
        return self.prefix + self.parent.name + self.postfix

    def __lshift__(self, new_value):
        self.update()
        self.kill = False
        if new_value == None:
            self.kill = True
        else:
            self.kill = False
            self.val = new_value
        self.lastChange = self.parent.core.now

    def __isub__(self, other):
        self.update()
        self.val = self.val - other
        self.lastChange = self.parent.core.now
        return self

    def __iadd__(self, other):
        self.update()
        self.val = self.val + 1
        self.lastChange = self.parent.core.now
        return self

    def __lt__(self, other):
        return self.val < other

    def __gt__(self, other):
        return self.val > other

    def __le__(self, other):
        return self.val <= other

    def __ge__(self, other):
        return self.val >= other

    def __eq__(self, other):
        return self.val == other

    def __ne__(self, other):
        return self.val != other

    def __add__(self, other):
        return self.val + other

    def __sub__(self, other):
        return self.val - other

    def __mul__(self, other):
        return self.val * other

    def __truediv__(self, other):
        return self.val / other

    def update(self):
        if """self.lastChange != self.parent.core.now""" and not self.kill:
            self.history.append(
                [
                    str(self.val),
                    self.getName(),
                    self.lastChange,
                    self.parent.core.now,
                ]
            )


class String:
    reserved = ["busy", "loading_active", "unloading_active"]

    def __init__(self, parent, prefix="", postfix=""):
        self.history = []
        self.val = []
        self.lastChange = 0
        self.name = parent.name
        self.prefix = prefix
        self.postfix = postfix
        parent.core.addTrace(self)
        self.core = parent.core

    def getName(self):
        return self.prefix + self.name + self.postfix

    def __lshift__(self, new_value):
        new_value = new_value.replace(" ", "")
        if not new_value in self.val:
            if not new_value in self.reserved:
                self.update()
                self.lastChange = self.core.now
            if new_value == "":
                self.val = []
            else:
                self.val.append(new_value)

    def __rshift__(self, new_value):
        new_value = new_value.replace(" ", "")
        if new_value in self.val:
            if not new_value in self.reserved:
                self.update()
                self.lastChange = self.core.now
            self.val.remove(new_value)

    def __eq__(self, other):
        if other == "":
            if len(self.val) == 0:
                return True
            return False
        elif other == None:
            return False
        other = other.replace(" ", "")
        return other in self.val

    def get(self):
        without_reserved = list(self.val)
        for res in self.reserved:
            if res in without_reserved:
                without_reserved.remove(res)
        if without_reserved == None:
            without_reserved = []
        return ", ".join(without_reserved)

    def update(self):
        if self.lastChange != self.core.now and self.get() != "":
            self.history.append(
                [
                    self.get(),
                    self.getName(),
                    self.lastChange,
                    self.core.now,
                ]
            )


class Zone(String):
    def __init__(self, name, prefix="", postfix=""):
        self.history = []
        self.val = []
        self.lastChange = 0
        self.name = name
        self.prefix = prefix
        self.postfix = postfix
        core.addTrace(self)
        self.core = core
