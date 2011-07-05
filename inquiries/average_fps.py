import numpy as np
import matplotlib.pyplot as plt
import os
from mirqi.core import inquiry
from mirqi.core import my_utils
import datetime

class Average_FPS(inquiry.Inquiry):
    NAME = u'Average FPS'
    DAYS_PER_PERIOD = inquiry.Inquiry_Parameter(7,"Days per period")

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

    def get_table(self):
        heading = [['Period Number'] + range(len(self.counts))]
        row = [['Period Start Date'] + self.start_dates]
        row1 = [['Averages'] + self.averages]
        row2 = [['Fluoro Event Counts'] + self.counts]
        row3 = [['Fluoro Frame Counts'] + self.frame_counts]
        return my_utils.transposed(heading + row +  row3 +  row2 + row1)

    def get_figure(self):
        fig = plt.figure()
        plt.scatter(range(len(self.averages)), self.averages, s= self.counts)
        plt.plot(range(len(self.averages)), self.averages, color='red')
        plt.xlabel('Period Number')
        plt.ylabel('Average FPS')
        plt.title("Average FPS Across All Events")
        plt.axis([0,len(self.counts)-1,5,15])
        return fig

    def get_text(self):
        out = "First event starts at " + str(self.first_time) + "\n"
        out += "Last event ends at " + str(self.last_time) + "\n"
        return out 


from mirqi.gui import report_writer

if __name__ == '__main__':
    procs = my_utils.get_procs('test')
    inq = Average_FPS(procs)
    report_writer.write_report([inq])
