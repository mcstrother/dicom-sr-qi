from srqi.core import inquiry
from srqi.core import my_utils
import matplotlib.pyplot as plt
import math


class Pause_Histogram(inquiry.Inquiry):
    NUM_BINS = inquiry.Inquiry_Parameter(30, "Number of Bins in Histogram")
    USE_LOG = inquiry.Inquiry_Parameter(True, "Plot log of pauses?")

    description = """Show a histogram of the length of pauses between fluoro events in procedures.

    Data Required:
        DICOM-SR .xml files

    """

    def run(self, sr_procs, context, extra_procs):
        pauses = []
        irradiation_ids = []
        for p in sr_procs:
            events = p.get_events()
            for i in range(1,len(events)):
                irradiation_ids.append(events[i].Irradiation_Event_UID)
                pause = my_utils.total_seconds(events[i].get_start_time()-events[i-1].get_end_time())
                if self.USE_LOG.value:
                    pause = math.log(pause)
                pauses.append(pause)
        self.pauses = pauses
        self.irradiation_ids = irradiation_ids

    def get_figures(self):
        fig = plt.figure()
        plt.hist(self.pauses, bins =self.NUM_BINS.value)
        plt.xlabel("Duration (Seconds)")
        plt.ylabel("Number of Pauses")
        plt.title("Duration of Intra-Procedure Pauses")
        return [fig]

    def get_tables(self):
        out = [["Irradiation Event UID", "Pause Length (seconds)", "Cumulative Percentage"]]
        p_list = sorted(zip(self.irradiation_ids, self.pauses), key = lambda x:x[1])
        for i in range(len(p_list)):
            out.append((p_list[i][0], p_list[i][1],
                        float(i)/(len(self.pauses)-1)
                        ))
        return [out]
            


