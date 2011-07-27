import numpy as np
import matplotlib.pyplot as plt
import os
from srqi.core import inquiry
from srqi.core import my_utils
import datetime


class Average_Fps(inquiry.Inquiry):
    NAME = u'Average FPS'
    DAYS_PER_PERIOD = inquiry.Inquiry_Parameter(7,"Days per period","the number \
of days to average over when reporting the average FPS. \
For example, setting the Days per period = 7 will show weekly averages. \
Periods are started counting from whenever the first irradiation event was \
recorded.")

    description = """Plots the average frames per second used in all procedures over time
    Plot also shows the number of irradiation events in each period.

    To compute the average, the Pulse_Rate of each fluoro event (non-fluor events
    are ignored) is multiplied by that event's duration. All of these are summed
    and the sum is divided by the total pedal time in the period.

    Data Required:
        DICOM-SR

    """

    def run(self, procs, context, extra_procs):
        events = [p.get_fluoro_events() for p in procs] 
        events = sum(events, []) #flatten from list of lists into single list of events
        first_time = min(events, key = lambda e: e.DateTime_Started).DateTime_Started
        last_time = max(events, key = lambda e: e.DateTime_Started).get_end_time()
        events_by_date = my_utils.organize(events, lambda e:e.DateTime_Started.date())
        current = first_time.date()
        averages =[]
        counts = []
        frame_counts = []
        start_dates = [current]
        while current <= last_time.date():
            es = []
            period_end = current + datetime.timedelta(days=self.DAYS_PER_PERIOD.value)
            while current < period_end:
                if current in events_by_date:
                    es = es + events_by_date[current]
                current = current + datetime.timedelta(days=1)
            start_dates.append(current)
            counts.append(len(es))
            frame_counts.append(sum([e.Number_of_Pulses for e in es]))
            if len(es) > 0:
                averages.append(my_utils.average_fps(es))
            else:
                averages.append(averages[-1])
        start_dates = start_dates[:-1]
        self.start_dates = start_dates
        self.averages = averages
        self.counts = counts
        self.frame_counts =frame_counts
        self.first_time = first_time
        self.last_time = last_time

    def get_tables(self):
        heading = [['Period Number'] + range(len(self.counts))]
        row = [['Period Start Date'] + self.start_dates]
        row1 = [['Averages'] + self.averages]
        row2 = [['Fluoro Event Counts'] + self.counts]
        row3 = [['Fluoro Frame Counts'] + self.frame_counts]
        return [my_utils.transposed(heading + row +  row3 +  row2 + row1)]

    def get_figures(self):
        fig = plt.figure()
        plt.scatter(range(len(self.averages)), self.averages, s= self.counts)
        plt.axis([0,len(self.counts)-1,5,16])
        axes = plt.gca()
        xtick_labels = []
        for i in axes.get_xticks():
            if i < len(self.start_dates):
                xtick_labels.append( self.start_dates[int(i)])
        axes.set_xticklabels(xtick_labels)
        #axes.set_xticklabels([self.start_dates[int(i)] for i in axes.get_xticks()])
        plt.plot(range(len(self.averages)), self.averages, color='red')
        plt.xlabel('Period Start Date')
        plt.ylabel('Average FPS')
        plt.title("Average FPS Across All Fluoro Events")
        fig.autofmt_xdate()
        return [fig]

    def get_text(self):
        out = "First event starts at " + str(self.first_time) + "\n"
        out += "Last event ends at " + str(self.last_time) + "\n"
        return out

    @classmethod
    def get_description(cls):
        return description


if __name__ == '__main__':
    inquiry.inquiry_main(Average_Fps)
