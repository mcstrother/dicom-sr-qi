import numpy as np
import matplotlib.pyplot as plt
import os

from mirqi.core import inquiry
from mirqi.core import my_utils

class Physician_Fps(inquiry.Inquiry):
    NAME = u'Physician FPS'
    DAYS_PER_PERIOD = inquiry.Inquiry_Parameter(7,"Days per period")
    #TODO implement parameters for start and end day
    DATE_RANGE_START = inquiry.get_standard_parameter("DATE_RANGE_START")
    DATE_RANGE_END = inquiry.get_standard_parameter("DATE_RANGE_END")

    description = """Average FPS over time, broken down by physician

    Shows separate plots of the Average FPS for each physician over time,
    as well as a group average.

    This is kept separate from the Average_FPS inquiry because it requires
    a Syngo data to mach which procedures in the DICOM-SR dataset were done
    by which physicians.

    Data required:
        DICOM-SR xml - procedures which cannot be matched with operators
            via the Syngo data are ignored. 
        Syngo - matched to the DICOM-SR data based on patient identifier
            numbers.

    """
    
    def run(self, procs, context, extra_procs):
        DAYS_PER_PERIOD = self.DAYS_PER_PERIOD.value
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

    def get_tables(self):
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
        return [out]

    def get_figures(self):
        figs = []
        for a, attending in enumerate(sorted(self.lookup.keys())):
            fig = plt.figure()
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
            figs.append(fig)
        return figs



    def get_text(self):
        out = "First event at " + str(self.first_time) + "\n"
        out += "Last event at " + str(self.last_start_time) + "\n"
        return out 

from mirqi.gui import report_writer
from mirqi.core import my_utils

if __name__ == '__main__':
    inquiry.inquiry_main(Physician_Fps)



