import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




class simCore:
    def __init__(self, startTime, maxTime):
        self.startTime = startTime
        self.objects = []
        self.maxTime = maxTime
        self.scheduler = [startTime]
    def run(self):
        while len(self.scheduler)>0:   
            self.scheduler = list(np.sort(self.scheduler))
            new_wake_times = []
            for obj in self.objects:
                wake_result = obj.wake(self.scheduler[0])
                if wake_result:
                    new_wake_times=new_wake_times+wake_result
            self.scheduler = self.scheduler[1:]
            self.scheduler = self.scheduler + new_wake_times
            self.scheduler = list(np.unique(np.array(self.scheduler)[np.array(self.scheduler)<self.maxTime]))
        for obj in self.objects:
            obj.end(self.maxTime)
    def addObject(self, obj):
        self.objects.append(obj)

    def addObjects(self, objects):
        for obj in objects:
            self.objects.append(obj)

    def getHistoryDf(self):
        history = []
        for obj in self.objects:
            history = history+obj.history
        df_history = pd.DataFrame(history)
        df_history.columns = ["action", "who", "start", "end"]
        return df_history

    def plotHistory(self, figsize=(10,5), start_plot = None,end_plot = None ):
        if start_plot == None:
            start_plot = self.startTime
        if end_plot == None: 
            end_plot = self.maxTime
        plotdata = self.getHistoryDf()
        plotdata = plotdata[~((plotdata["start"]<start_plot) & (plotdata["end"]<start_plot) | (plotdata["start"]>end_plot) & (plotdata["end"]>end_plot))]
        plotdata["end"] = [min(x, end_plot) for x in plotdata["end"]]
        plotdata["start"] = [max(x, start_plot) for x in plotdata["start"]]
        whos = np.unique(plotdata["who"])
        #Define Plot Colors
        cm = plt.get_cmap('gist_rainbow')
        all_actions = np.unique(plotdata["action"])
        all_actions = all_actions[[not str.isnumeric(x) for x in all_actions]]
        colors = [cm(x) for x in np.linspace(0,1,len(all_actions))]
        col_dict = {}
        _=[col_dict.update({cap:col})  for cap, col in zip(all_actions,colors )]


        def plotLineSet(y, x_data, captions, col_dict):
            x_data = x_data.T
            y_data=np.zeros(x_data.shape)+y

            if not str.isnumeric(captions.iloc[0]):    #Everything but Buffers:
                for cap in np.unique(captions):
                    mask = (captions == cap)
                    ax = plt.plot(x_data[:,mask], y_data[:,mask],marker = "|", color = col_dict[cap])
                for s, e in x_data.T:
                    plt.text(s,y+0.1,str(int((e-s) )), rotation = 'vertical')
            else:    #Buffers:
                for cap in np.unique(captions):
                    mask = (captions == cap)
                    ax = plt.plot(x_data[:,mask], y_data[:,mask]-0.5+0.1*int(cap), color = 'black')
                for [s, e], cap in zip(x_data.T, captions):
                    plt.text(s,y-0.5+0.1*int(cap),cap, rotation = 'horizontal')

        i = 0
        plt.figure(figsize = figsize)
        for who in whos:
            plotdata_tmp = plotdata[plotdata["who"]==who]
            x_data = plotdata_tmp[["start","end"]].values
            capts = plotdata_tmp["action"]
            plotLineSet(i,x_data, capts, col_dict)
            i = i+1

        for key, item in col_dict.items():
            plt.plot(self.startTime,0,label=key, marker = "|",color = item)
        plt.yticks(range(i), whos)
        plt.legend()
        plt.show()


class simObject:
    def __init__(self, name):
        self.name = name
        self.startTime = None
        self.eventQuene = []
        self.history = []
    def wake(self, time):
        return False
    def end(self):
        return




class rob(simObject):
    def __init__(self, name):
        super().__init__(name)
        self.programs = []
        self.busy = False
        self.state = ""

    def add_programm(self,program):
        program.rob = self
        self.programs.append(program)

    def wake(self, time):
        wake_times = False
        if self.busy:
            for prog in self.programs:
                if prog.active:
                    wake_times = prog.finish(time)
                    break
        elif not self.busy:
            for prog in self.programs:
                wake_times = prog.start(time)
                if wake_times:
                    break
        if not wake_times == False:
            return wake_times+[time]
        return False
    
    def end(self, time):
        for prog in self.programs:
            if prog.active:
                prog.end(time)


class buffer(simObject):
    def __init__(self, name, capacity, partList):
        super().__init__(name)
        self.max_parts = capacity
        self.parts = partList
        self.lastChange = 0

    def updateHist(self, time):
        #action, who, start, end
        self.history.append([
            str(len(self.parts)),
            self.name,
            self.lastChange,
            time
        ])
        self.lastChange = time
        
    def receive(self, part, time):
        if len(self.parts) < self.max_parts:
            self.updateHist(time)
            self.parts.append(part)
            return True
        else:
            return False

    def give(self, time):
        if len(self.parts)>0:
            self.updateHist(time)
            part = self.parts[0]
            self.parts = self.parts[1:]
            return part
        return False

    def end(self, time):
        self.updateHist(time)


class jig(buffer):
    def __init__(self, name):
        super().__init__(name, 1, [])


