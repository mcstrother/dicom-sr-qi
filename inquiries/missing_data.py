import assess_procedure
import datetime
import my_utils
import matplotlib.pyplot as plt

class Missing_Data(assess_procedure.Inquiry):
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
        return [ ["Period Start Date"] + self.starts, ["Procedure Count"] +self.counts]


    def get_figure(self):
        fig = plt.figure(1)
        plt.plot(self.starts, self.counts)
        return fig
    
            
                

    
