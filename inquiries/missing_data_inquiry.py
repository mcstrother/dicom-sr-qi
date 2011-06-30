from mirqi.core import inquiry, my_utils
import datetime
import matplotlib.pyplot as plt

class Missing_Data_Inquiry(inquiry.Inquiry):
    """An inquiry to look for days of missing data
    by simply plotting the number of procedures per day
    over time
    """

    def run(self, procs, context):
        DAYS_PER_PERIOD = 1
        orgd_procs = my_utils.organize(procs, key = lambda x: x.StudyDate)
        delta = datetime.timedelta(days = DAYS_PER_PERIOD)
        start = min(procs, key = lambda p:p.StudyDate).StudyDate
        last_proc = max(procs, key = lambda p: p.StudyDate)
        counts = []
        starts = []
        one_day = datetime.timedelta(days=1)
        while start < last_proc.StudyDate:
            count =0
            starts.append(start)
            current = start
            while current < start + delta:
                if current in orgd_procs:
                    count = count + len(orgd_procs[current])
                current = current + one_day
            counts.append(count)
            start = start+delta
        self.counts = counts
        self.starts = starts


    def get_table(self):
        return my_utils.transposed([ ["Period Start Date"] + self.starts, ["Procedure Count"] +self.counts])


    def get_figure(self):
        fig = plt.figure()
        colors = []
        for day in self.starts:
            if day.weekday() == 5 or day.weekday() == 6:
                colors.append('r')
            else:
                colors.append('b')
        plt.scatter(self.starts,self.counts,c=colors)
        fig.autofmt_xdate()
        return fig
    
            
                
from mirqi.gui import report_writer
from mirqi.core import my_utils

if __name__ == '__main__':
    procs = my_utils.get_procs('test')
    inq = Missing_Data_Inquiry(procs)
    report_writer.write_report([inq])


    
