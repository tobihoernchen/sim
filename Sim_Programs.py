import Sim_Tools as tools

class rob_handling_program_easy:
    def __init__(self, name, duration, take_from, place_at):
        self.name = name
        self.duration = duration
        self.take_from = take_from
        self.place_at = place_at
        self.rob = None
        self.start_time = 0
        self.end_time = 0
        self.active = False
        self.part = None
    def start(self, start_time):
        take_result = self.take_from.give(start_time)
        if take_result:
            self.part = take_result
            self.rob.busy = True
            self.start_time=start_time
            self.active = True
            self.end_time = start_time+self.duration
            return [start_time+self.duration]
        return False
    def finish(self, time):
        if time >= self.end_time:
            receive_result = self.place_at.receive(self.part, time)
            if receive_result:
                self.part = None
                self.rob.busy = False
                self.active = False
                #action, who, start, end
                self.rob.history.append([
                    self.name,
                    self.rob.name,
                    self.start_time,
                    time
                ])
                return []
        return False
    def end(self, time):
        self.rob.history.append([
            self.name,
            self.rob.name,
            self.start_time,
            time
        ])

class rob_handling_program_advanced:
    def __init__(self, name, duration, take_from, place_at):
        self.name = name
        self.duration = duration
        self.take_from = take_from
        self.place_at = place_at
        self.rob = None
        self.start_time = 0
        self.end_time = 0
        self.active = False
        self.part = None
    def start(self, start_time):
        take_result = self.take_from.give(start_time)
        if take_result:
            self.part = take_result
            self.rob.busy = True
            self.start_time=start_time
            self.active = True
            self.end_time = start_time+self.duration
            return [start_time+self.duration]
        return False
    def finish(self, time):
        if time >= self.end_time:
            receive_result = self.place_at.receive(self.part, time)
            if receive_result:
                self.part = None
                self.rob.busy = False
                self.active = False
                #action, who, start, end
                self.rob.history.append([
                    self.name,
                    self.rob.name,
                    self.start_time,
                    time
                ])
                return []
        return False
    def end(self, time):
        self.rob.history.append([
            self.name,
            self.rob.name,
            self.start_time,
            time
        ])
