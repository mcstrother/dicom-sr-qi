from mirqi.core import inquiry, my_utils
import datetime
import matplotlib.pyplot as plt



class Missing_Data_Inquiry(inquiry.Inquiry):

    description = """Plot to look for days from which you might be missing data

    Shows the number of DICOM-SR procedures reported for each day from the
    beginning to the end of your data set. Weekends are highlighted in red.
    A sudden decline in the number of procedures over a period of a few days
    may suggest that you are missing SR data for those days.

    Data Required:
        DICOM-SR xml

    Parameters:
        None

    """
    NAME = u'Missing Data Inquiry'
    START_DATE = inquiry.Inquiry_Parameter(datetime.date.today()-datetime.timedelta(days=365), "Start Date")
    

    def run(self, procs, context, extra_procs):
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


    def get_tables(self):
        return [my_utils.transposed([ ["Period Start Date"] + self.starts, ["Procedure Count"] +self.counts])]


    def get_figures(self):
        fig = plt.figure()
        colors = []
        for day in self.starts:
            if day.weekday() == 5 or day.weekday() == 6:
                colors.append('r')
            else:
                colors.append('b')
        plt.scatter(self.starts,self.counts,c=colors)
        plt.title("Number of Procedure Records Per Day")
        plt.xlabel("Days (red = weekends)")
        plt.ylabel("Number of Procedures Records")
        fig.autofmt_xdate()
        return [fig]

    
            
                
from mirqi.gui import report_writer
from mirqi.core import my_utils

if __name__ == '__main__':
    inquiry.inquiry_main(Missing_Data_Inquiry)


    
