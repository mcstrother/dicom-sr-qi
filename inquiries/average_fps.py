import numpy as np
import matplotlib.pyplot as plt
import os
import mirqi.core.assess_procedure
from mirqi.core import my_utils
import datetime

class Average_FPS(mirqi.core.assess_procedure.Inquiry):

    DAYS_PER_PERIOD = 7

    def run(self, procs, context):
        events = [p.get_events() for p in procs]
        events = sum(events, []) #flatten from list of lists into single list of events
        first_time = min(events, key = lambda e: e.DateTime_Started).DateTime_Started
        last_time = max(events, key = lambda e: e.DateTime_Started).get_end_time()
        events_by_date = my_utils.organize(events, lambda e:e.DateTime_Started.date())
        current = first_time.date()
        averages =[]
        counts = []
        start_dates = [current]
        while current <= last_time.date():
            es = []
            period_end = current + datetime.timedelta(days=self.DAYS_PER_PERIOD)
            while current < period_end:
                if current in events_by_date:
                    es = es + events_by_date[current]
                current = current + datetime.timedelta(days=1)
            counts.append(len(es))
            averages.append(my_utils.average_fps(es))
            start_dates.append(current)
        start_dates = start_dates[:-1]
        self.start_dates = start_dates
        self.averages = averages
        self.counts = counts
        self.first_time = first_time
        self.last_time = last_time

    def get_table(self):
        heading = [['Period Number'] + range(len(self.counts))]
        row = [['Period Start Date'] + self.start_dates]
        row1 = [['Averages'] + self.averages]
        row2 = [['Event Counts'] + self.counts]
        return my_utils.transposed(heading + row+ row1 + row2)

    def get_figure(self):
        fig = plt.figure(1)
        plt.scatter(range(len(self.averages)), self.averages, s= self.counts)
        plt.plot(range(len(self.averages)), self.averages, color='red')
        plt.xlabel('Period Number')
        plt.ylabel('Average FPS')
        plt.title("Average FPS Across All Events")
        plt.axis([0,len(self.counts)-1,5,15])
        return fig

    def get_name(self):
        return u'Average FPS'

    def get_text(self):
        out = "First event starts at " + str(self.first_time) + "\n"
        out += "Last event ends at " + str(self.last_time) + "\n"
        return out 


from mirqi.gui import report_writer

if __name__ == '__main__':
    procs = my_utils.get_procs('bjh')
    inq = Average_FPS(procs)
    report_writer.write_report([inq])
