import numpy as np
import matplotlib.pyplot as plt
import os

import mirqi.core.Inquiry
from mirqi.core import my_utils

class Physician_FPS(mirqi.core.Inquiry.Inquiry):
    NAME = u'Physician FPS'
    DAYS_PER_PERIOD = 7
    #TODO implement parameters for start and end day
    
    def run(self, procs, context):
        DAYS_PER_PERIOD = self.DAYS_PER_PERIOD
        procs = [p for p in procs if p.is_pure()]
        procs_by_attending = my_utils.organize(procs, lambda x: x.get_syngo().rad1.replace(',',''))

        first_time = min(procs, key = lambda x: x.get_start_time()).get_start_time()
        last_start_time = max(procs, key = lambda x: x.get_start_time()).get_start_time()
        self.num_periods = int((last_start_time - first_time).days/DAYS_PER_PERIOD)
        self.first_time = first_time
        self.last_start_time =last_start_time
        
        out = {}
        for attending, procs in procs_by_attending.iteritems():
            events = [p.get_events() for p in procs]
            events = sum(events, [])# flatten from list of lists to list of events
            events = [e for e in events if e.Irradiation_Event_Type == "Fluoroscopy"]
            events_by_period = my_utils.organize(events,
                                                 lambda e: int((e.get_start_time() - first_time).days/DAYS_PER_PERIOD))
            out[attending] = events_by_period            

        self.lookup = out #lookup[attending][period_number] --> [events]

    def _get_individual_table(self):
        attending_list = sorted(self.lookup.keys())
        dimension = (self.num_periods ,len(attending_list))
        average_table =np.zeros(dimension).tolist()
        count_table = np.zeros(dimension).tolist()
        for a, attending in enumerate(attending_list):
            for period in range(self.num_periods-1):
                if period in self.lookup[attending]:
                    events = self.lookup[attending][period]
                    count = len(events)
                    average = my_utils.average_fps(events)
                    count_table[period][a] = count
                    average_table[period][a] = average
                else:
                    count_table[period][a] = 0
                    average_table[period][a] = ''
        out = [[''] + attending_list + [''] + attending_list] #heading of table
        for r in range(len(average_table)):
            row = [r] + average_table[r] + [''] + count_table[r]
            out.append(row)
        out = my_utils.transposed(out)
        return out

    def get_table(self):
        return self._get_individual_table()


    def _get_individual_figure(self):
        num_attendings = len(self.lookup.keys())
        fig = plt.figure(1)
        for a, attending in enumerate(sorted(self.lookup.keys())):
            plt.subplot(num_attendings+1, 1,a)
            plt.axis([0,self.num_periods,5,15])
            plt.xlabel('Period Number')
            plt.ylabel('Average FPS')
            plt.title(attending)
            x = []
            y = []
            s = []
            for period, events in self.lookup[attending].iteritems():
                x.append(period)
                y.append(my_utils.average_fps(events))
                s.append(len(events))
            plt.scatter(x,y,s=s,label=attending)
            plt.plot(x,y,color='red')
        plt.plot(num_attendings+1, 1, num_attendings+1)
        return fig

    def get_figure(self):
        return self._get_individual_figure()


    def get_text(self):
        out = "First event at " + str(self.first_time) + "\n"
        out += "Last event at " + str(self.last_start_time) + "\n"
        return out 

from mirqi.gui import report_writer
from mirqi.core import my_utils

if __name__ == '__main__':
    procs = [p for p in my_utils.get_procs('bjh') if p.is_pure()]
    inq = Physician_FPS(procs)
    report_writer.write_report([inq])



