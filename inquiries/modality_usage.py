from srqi.core import inquiry, my_utils

def get_period_sum(period, val_func, event_types = ()):
    """
    Parameters:
        period : a list of Events
        val_func : a function that takes an Event and returns the value of
            the event to be summed. For example `lambda x:x.Dose_RP` would be
            a valid and logical input for this parameter
        event_type : an iterable of strings. sums over only Events of these
            Irradiation_Event_Types. If bool(event_type) == False then sums
            over all events. If you pass a basestring, it wil automatically
            be converted to an iterable for you.
    """
    if isinstance(event_types, basestring):
        event_types = (event_types)
    total = 0
    for event in period:
        if not event_types or event.Irradiation_Event_Type in event_types:
            total = total + val_func(event)
    return total


class Modality_Usage(inquiry.Inquiry):
    name = "Modality Usage"
    description = """Describe amount of usage of different modalities across data set

    Includes plots of number of events, number of frames, and dose as well
    as tabular output.
    It should be noted that this metric will be sensitive to case mix.

    Data required:
        DICOM-SR
    """
    PERIOD_LEN = inquiry.get_standard_parameter('PERIOD_LEN')

    def run(self, sr_procs, context, extra_procs):
        sr_procs, period_starts = my_utils.periodize_by_date(sr_procs,
                                                      self.PERIOD_LEN.value,
                                                      date_key = lambda p:p.StudyDate)
        events_by_period = []
        for period in sr_procs:
            period_events = []
            for proc in period:
                period_events = period_events + proc.get_events()
            events_by_period.append(period_events)
        self.events_by_period = events_by_period
        self.period_starts = period_starts
        get_dose = lambda e:e.Dose_RP
        self.fluoro_doses = [get_period_sum(period,get_dose,"Fluoroscopy") for period in self.events_by_period]
        self.acquisition_doses = [get_period_sum(period,
                                            get_dose,"Stationary Acquisition") for period in self.events_by_period]
        self.total_doses = [get_period_sum(period,get_dose) for period in self.events_by_period]
        get_frames = lambda e:e.Number_of_Pulses
        self.fluoro_frames = [get_period_sum(period,get_frames, "Fluoroscopy") for period in self.events_by_period]
        self.acquisition_frames = [get_period_sum(period, get_frames, "Stationary Acquisition") for period in self.events_by_period]
        self.total_frames = [get_period_sum(period, get_frames) for period in self.events_by_period]
        count = lambda e:1
        self.fluoro_events = [get_period_sum(period, count, "Fluoroscopy") for period in self.events_by_period]
        self.acquisition_events = [get_period_sum(period, count, "Stationary Acquisition") for period in self.events_by_period]
        self.total_events = [get_period_sum(period,count) for period in self.events_by_period]

    def get_figures(self):
        import matplotlib.pyplot as plt
        figs = []
        fig = plt.figure()
        plt.title("Dose By Modality")
        plt.ylabel("Dose")
        plt.xlabel("Period Start")
        plt.plot(self.period_starts,self.fluoro_doses, label = "Fluoro")
        plt.plot(self.period_starts,self.acquisition_doses, label = "Acquisition")
        plt.plot(self.period_starts,self.total_doses, label = "Total Dose")
        fig.autofmt_xdate()
        plt.legend()
        figs.append(fig)
        #bar chart of procedure numbers
        fig = plt.figure()
        plt.title("Number of Events Per Period")
        plt.bar(self.period_starts,
                [len(period) for period in self.events_by_period],
                align = 'center')
        plt.xlabel("Period Start")
        plt.ylabel("Number of Events")
        fig.autofmt_xdate()
        figs.append(fig)
        # event numbers
        fig = plt.figure()
        plt.title("Event Counts")
        plt.ylabel("Number of Events")
        plt.xlabel("Period Start")
        plt.plot(self.period_starts,self.fluoro_events, label = "Fluoro")
        plt.plot(self.period_starts,self.acquisition_events, label = "Acquisition")
        plt.plot(self.period_starts,self.total_events, label = "Total Events")
        fig.autofmt_xdate()
        plt.legend()
        figs.append(fig)
        # plot acquisition event numbers on separate graph for readability
        fig = plt.figure()
        plt.title("Acquisition Event Counts")
        plt.ylabel("Number of Events")
        plt.xlabel("Period Start")
        plt.plot(self.period_starts,self.acquisition_events, label = "Acquisition")
        fig.autofmt_xdate()
        plt.legend()
        figs.append(fig)
        # frame counts
        fig = plt.figure()
        plt.title("Frame Counts")
        plt.ylabel("Number of Frames")
        plt.xlabel("Period Start")
        plt.plot(self.period_starts,self.fluoro_frames, label = "Fluoro")
        plt.plot(self.period_starts,self.acquisition_frames, label = "Acquisition")
        plt.plot(self.period_starts,self.total_frames, label = "Total")
        fig.autofmt_xdate()
        plt.legend()
        figs.append(fig)
        # acquisition frame counts
        fig = plt.figure()
        plt.title("Acquisition Frame Counts")
        plt.ylabel("Number of Frames")
        plt.xlabel("Period Start")
        plt.plot(self.period_starts,self.acquisition_frames, label = "Acquisition")
        fig.autofmt_xdate()
        plt.legend()
        figs.append(fig)
        return figs


    def get_tables(self):
        heading =["Period Start", "Fluoro Dose RP (GY)", "Acquisition Dose", "Total Dose",
                  "Fluoro Frames", "Acquisition Frames", "Total Frames",
                  "Fluoro Events", "Acquisition Events", "Total Events"]
        import numpy as np
        values = np.vstack((self.period_starts, self.fluoro_doses, self.acquisition_doses,
                   self.total_doses,
                   self.fluoro_frames, self.acquisition_frames, self.total_frames,
                   self.fluoro_events, self.acquisition_events, self.total_events))
        out = [heading] + values.transpose().tolist()
        return [out]
        




                     
