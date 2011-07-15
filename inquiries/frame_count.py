from srqi.core import inquiry
import datetime

#The name of the class must be the same as the file name, except
#with the first letter of each word capitalized.
class Frame_Count(inquiry.Inquiry): #all inquiries inherit from inquiry.Inquiry
    # "NAME" and "description" are standard class variables that are used to
    # provide information to the user. If you don't specify them, they will
    # be replaced by reaonable defaults.
    NAME = "Frame Counter" 
    description = """Counts the number of frames in each procedure

    Data required:
        DICOM-SR xml

    Parameters:
        START_DATE - limit the procedures analyzed to those after this date
    """
    # Define a parameter called START_DATE that is to be specified by the user.
    # The first argument of the Inquiry_Parameter constructor is a default value
    # and the second is an optional human-readable name for the parameter.
    START_DATE = inquiry.Inquiry_Parameter(datetime.date.today(), "Start Date")
    

    def run(self, sr_procs, context, extra_procs):
        # do some trivial "analysis" of the procedures by calling some
        # convenience methods proceded by the Read_XML.Procedure objects
        self.frame_counts = []
        self.start_times = []
        for proc in sr_procs:
            if not len(proc.get_events()) ==0 \
               and proc.get_start_time().date() > self.START_DATE.value: #note the .value part of this
                self.frame_counts.append(proc.get_number_of_pulses())
                self.start_times.append(proc.get_start_time())


    def get_text(self):
        # Return a string to be shown to the user as part of the output
        return "There are a total of " + str(len(self.frame_counts)) + " procedures in the input file"

    def get_figures(self):
        # return a list of matplotlib figure objects that will be
        # saved and rendered
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.scatter(self.start_times, self.frame_counts)
        plt.title("Frame counts over time.")
        plt.xlabel("Start Time of Procedure")
        plt.ylabel("Number of Frames")
        return [fig]

    def get_tables(self):
        # make a demo_table demonstrating the basic idea of making a table
        # out of an iterable of iterables (in this case, a list of tuples)
        demo_table = [("Row0 Col0", "Row0 Col1"), ("Row1 Col0", "Row1 Col1")]
        assert(demo_table[0][1] == "Row0 Col1")
        assert(demo_table[1][1] == "Row1 Col1")
        # make a more useful table
        # the function call `zip(self.start_times, self.frame_counts)`
        # creates a list of tuples that looks like
        # [ (start_time1, frame_count1),
        #   (start_time2, frame_count2),
        #   (start_time3, frame_count3),...]
        table1 = zip(self.start_times, self.frame_counts)
        heading = [("Start Times", "Frame Counts")]
        table1 = heading  + table1
        return [demo_table, table1]
        


