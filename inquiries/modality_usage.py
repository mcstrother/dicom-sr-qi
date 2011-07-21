from srqi.core import inquiry, my_utils

class Modality_Usage(inquiry.Inquiry):
    name = "Modality Usage"
    description = """Describe amount of usage of different modalities across data set

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

    def get_figures(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.title("Dose By Modality")
        plt.ylabel("Dose")
        plt.xlabel("Period Start")
        fluoro_doses = []
        acquisition_doses = []
        total_doses = []
        for period in self.events_by_period:
            fluoro_dose = 0
            acquisition_dose = 0
            total_dose = 0
            for e in period:
                total_dose = total_dose+e.Dose_RP
                if e.Irradiation_Event_Type == "Fluoroscopy":
                    fluoro_dose = fluoro_dose+e.Dose_RP
                elif e.Irradiation_Event_Type =='Stationary Acquisition':
                    acquisition_dose = acquisition_dose+e.Dose_RP
            fluoro_doses.append(fluoro_dose)
            acquisition_doses.append(acquisition_dose)
            total_doses.append(total_dose)
        plt.plot(self.period_starts,fluoro_doses, label = "Fluoro")
        plt.plot(self.period_starts,acquisition_doses, label = "Acquisition")
        plt.plot(self.period_starts,total_doses, label = "Total Dose")
        fig.autofmt_xdate()
        plt.legend()
        return [fig]




                     
