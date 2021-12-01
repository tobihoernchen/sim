import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


class simCore:
    def __init__(self):
        self.objects = []
        self.now = None
        self.traces = []

    def run(self, startTime, maxTime):
        self.startTime = startTime
        self.maxTime = maxTime
        self.scheduler = [startTime]
        # run while events are scheduled
        while len(self.scheduler) > 0:
            # take the soonest event
            self.scheduler = list(np.sort(self.scheduler))
            self.now = self.scheduler[0]
            # wake all objects (the schedule themselves)
            for obj in self.objects:
                obj.wake()
            self.scheduler = self.scheduler[1:]
            self.scheduler = list(
                np.unique(
                    np.array(self.scheduler)[np.array(self.scheduler) < self.maxTime]
                )
            )
        self.now = self.maxTime
        for obj in self.objects:
            obj.end()

    def addObject(self, obj):
        obj.core = self
        self.objects.append(obj)

    def addObjects(self, objects):
        for obj in objects:
            self.addObject(obj)

    def addTrace(self, trace):
        self.traces.append(trace)

    def getAllTraces(self):
        return [trace.getName() for trace in self.traces]

    def getHistoryDf(self, start_plot, end_plot, names=None, excludes=None):
        history = []
        for trace in self.traces:
            if names != None and not trace.getName() in names:
                continue
            if excludes != None and any(
                [exclude in trace.getName() for exclude in excludes]
            ):
                continue
            history = history + trace.history
        df_history = pd.DataFrame(history)
        if len(history) > 0:
            df_history.columns = ["action", "who", "start", "end"]
            df_history = df_history[
                ~(
                    (df_history["start"] < start_plot)
                    & (df_history["end"] < start_plot)
                    | (df_history["start"] > end_plot) & (df_history["end"] > end_plot)
                )
            ]
            df_history["end"] = [min(x, end_plot) for x in df_history["end"]]
            df_history["start"] = [max(x, start_plot) for x in df_history["start"]]

        return df_history

    def plotHistory(self, start_plot=None, end_plot=None, names=None, excludes=None):
        if start_plot == None:
            start_plot = self.startTime
        if end_plot == None:
            end_plot = self.maxTime
        data = self.getHistoryDf(start_plot=start_plot, end_plot=end_plot)

        data["duration"] = data["end"] - data["start"]
        whos = list(data["who"].unique())
        mins = {}
        maxs = {}

        visible = [True for _ in whos]
        if excludes != None:
            visible = [not any([ex in who for ex in excludes]) for who in whos]
        if names != None:
            visible = [who in names for who in whos]

        whos = list(np.array(whos)[visible])

        data["y"] = [whos.index(x) if x in whos else -1 for x in data["who"]]
        for y, who in zip(range(len(whos)), whos):
            if data[data["who"] == who]["action"].values[0].isnumeric():
                mins.update({y: min(data[data["who"] == who]["action"].astype(int))})
                maxs.update({y: max(data[data["who"] == who]["action"].astype(int))})

        plot_x = []
        plot_y = []
        plot_texts = []
        plot_tags = []
        margin = 0.5
        for s, e, y, a in zip(data["start"], data["end"], data["y"], data["action"]):
            if y != -1:
                plot_x.extend([s, e, None])
                if a.isnumeric():
                    if (maxs[y] - mins[y]) > 0:
                        val = (int(a) - mins[y]) / (maxs[y] - mins[y])
                    else:
                        val = int(a) - mins[y]
                    y = y + (val - 0.5) * margin
                    plot_y.extend([y, y, None])
                    plot_texts.extend([a, "", ""])
                    plot_tags.extend(["numeric", "numeric", "numeric"])
                else:
                    plot_y.extend([y, y, None])
                    plot_texts.extend([str(e - s), "", ""])
                    plot_tags.extend([a, a, a])

        plotdata = pd.DataFrame(
            list(zip(plot_x, plot_y, plot_texts, plot_tags)),
            columns=["x", "y", "text", "tag"],
        )

        fig = px.line(plotdata, x="x", y="y", text="text", color="tag", orientation="v")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        fig.update_layout(
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(len(whos))),
                ticktext=whos,
                fixedrange=False,
            )
        )
        fig.update_traces(textposition="top center")
        fig.show()


"""
    def plotHistory(
        self, figsize=(10, 5), start_plot=None, end_plot=None, names=None, excludes=None
    ):
        if start_plot == None:
            start_plot = self.startTime
        if end_plot == None:
            end_plot = self.maxTime

        plotdata = self.getHistoryDf(names, excludes)
        plotdata["duration"] = plotdata["end"] - plotdata["start"]

        # filter for time to plot
        plotdata = plotdata[
            ~(
                (plotdata["start"] < start_plot) & (plotdata["end"] < start_plot)
                | (plotdata["start"] > end_plot) & (plotdata["end"] > end_plot)
            )
        ]
        plotdata["end"] = [min(x, end_plot) for x in plotdata["end"]]
        plotdata["start"] = [max(x, start_plot) for x in plotdata["start"]]

        whos = np.unique(plotdata["who"])
        # Define Plot Colors
        cm = plt.get_cmap("gist_rainbow")
        all_actions = np.unique(plotdata["action"])
        all_actions = all_actions[[not str.isnumeric(x) for x in all_actions]]
        colors = [cm(x) for x in np.linspace(0, 1, len(all_actions))]
        col_dict = {}
        _ = [col_dict.update({cap: col}) for cap, col in zip(all_actions, colors)]

        def plotLineSet(y, x_data, captions, col_dict):
            x_data = x_data.T
            y_data = np.zeros(x_data.shape) + y

            if not str.isnumeric(captions.iloc[0]):  # Everything but Buffers:
                for cap in np.unique(captions):
                    mask = captions == cap
                    ax = plt.plot(
                        x_data[:, mask],
                        y_data[:, mask],
                        marker="|",
                        color=col_dict[cap],
                    )
                for s, e in x_data.T:
                    plt.text(s, y + 0.1, str(e - s), rotation="vertical")
            else:  # Buffers:
                maximum = max([int(cap) for cap in np.unique(captions)]) + 0.01
                for cap in np.unique(captions):
                    mask = captions == cap
                    ax = plt.plot(
                        x_data[:, mask],
                        y_data[:, mask] - 0.5 + 0.8 * int(cap) / maximum,
                        color="black",
                    )
                for [s, e], cap in zip(x_data.T, captions):
                    plt.text(
                        s,
                        y - 0.5 + 0.8 * int(cap) / maximum,
                        cap,
                        rotation="horizontal",
                    )

        i = 0
        plt.figure(figsize=figsize)
        for who in whos:
            plotdata_tmp = plotdata[plotdata["who"] == who]
            x_data = plotdata_tmp[["start", "end"]].values
            capts = plotdata_tmp["action"]
            plotLineSet(i, x_data, capts, col_dict)
            i = i + 1

        for key, item in col_dict.items():
            plt.plot(self.startTime, 0, label=key, marker="|", color=item)
        plt.yticks(range(i), whos)
        plt.legend()
        plt.show()

"""
core = simCore()
