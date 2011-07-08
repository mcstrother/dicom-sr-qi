from mirqi.core import inquiry, my_utils, my_exceptions
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import datetime



class Room_Usage(inquiry.Inquiry):
    resolution = inquiry.Inquiry_Parameter(600, "Seconds Per Period")
    description = """Visualizes distribution of fluoro machine usage in a week

    For each procedure, define the fluoro machine as "in use"
    between the first and last irradiation event of the
    procedure. Then divide the days of the week
    into periods and count how many times that
    fluoro machine is in use on that period of that
    day of the week.


    Data Required:
        DICOM-SR xml - assumes that all procedures are from a single fluoro machine.

    Parameters:
        Seconds per period

    """

    def _add_period(self, table, weekday, start_seconds, end_seconds):
        """table[weekday][block]
        start_seconds and end_seconds are ints
        """
        first_block = int(start_seconds/self.resolution.value)
        last_block = int((end_seconds-1)/self.resolution.value)
        for block in range(first_block, last_block+1):
            table[weekday][block] = table[weekday][block] +1
        
    def run(self, procs, context, extra_procs):
        num_blocks = 24*60*60 / self.resolution.value # if day isn't evenly divisible, last block will be slightly longer
        table = []
        for i in range(7):
            table.append([0]*num_blocks)
        #table[weekday][block]
        for proc in procs:
            try:
                start_time= proc.get_start_time()
            except my_exceptions.DataMissingError:
                continue
            start_seconds = (start_time.hour * 60 + start_time.minute)*60
            end_time = proc.get_end_time()
            end_seconds = (end_time.hour * 60 + end_time.minute)*60
            if start_time.weekday() == end_time.weekday():
                self._add_period(table,start_time.weekday(), start_seconds,end_seconds)
            elif (start_time.weekday()+1)%7 == end_time.weekday():
                self._add_period(table,start_time.weekday(),start_seconds,86400)#86400= number of seconds in a day
                self._add_period(table,end_time.weekday(),0,end_seconds)
            else:
                raise RuntimeError("This should not have happened")
        self._table = table


    def get_tables(self):
        return [my_utils.transposed(self._table)]

    def get_figures(self):
        a = np.array(self._table)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cax = ax.matshow(a.transpose(), cmap=cm.get_cmap('gray_r'), aspect='auto')
        max_count = a.max()
        cbar = fig.colorbar(cax, ticks = [0,int(max_count/3), int((max_count*2)/3), max_count])
        cbar.set_label("Number of Procedures")
        plt.grid(False)

        #change the labels
        old_labels = [0,0,20,40,60,80,100,120,140]
        old_yticklabels = plt.gca().get_yticklabels()
        print [y.get_text() for y in old_yticklabels]
        print dir(old_yticklabels[0])
        new_labels = []
        for x in old_labels:
                seconds = x*self.resolution.value
                hours = int(seconds/3600)
                minutes = int((seconds -hours*3600)/60)
                seconds = int(seconds - (hours*60+minutes)*60)
                new_labels.append(str(datetime.time(hour = hours, minute = minutes, second=seconds)))
        plt.gca().set_yticklabels(new_labels)
        plt.gca().set_xticklabels(['','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], size='small')
        plt.title("Usage of BJH Room 812")
        plt.xlabel("Day of week (Monday - Sunday)")
        plt.ylabel("Time of Day (block number)")
        return [fig]


from mirqi.gui import report_writer

if __name__ == '__main__':
    inquiry.inquiry_main(Room_Usage, 'slch')
