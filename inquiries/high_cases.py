from srqi.core import inquiry
import matplotlib.pyplot as plt
import numpy as np

def get_accumulation_fig(proc):
    fig = plt.figure()
    plt.title("Accumulation During Procedure for Patient " + str(proc.PatientID) + " on " + str(proc.StudyDate))
    # plot doses
    dose_ax = plt.subplot(211)
    dose_ax.plot([e.DateTime_Started for e in proc.get_events()],
                 np.cumsum([e.Dose_RP for e in proc.get_events()])
                 )
    plt.ylabel('Dose (Gy)')
    # plot frames
    frames_ax = plt.subplot(212, sharex = dose_ax)
    frames_ax.plot([e.DateTime_Started for e in proc.get_events()],
                   np.cumsum([e.Number_of_Pulses for e in proc.get_events()])
                   )
    plt.ylabel('# of Frames')
    fig.autofmt_xdate()
    return fig


class High_Cases(inquiry.Inquiry):
    NAME = "High Cases"
    description = """Finds and analyzes cases where the dose exceeds a specified limit 

    Data required:
        DICOM-SR xml
    """
    LIMIT = inquiry.Inquiry_Parameter(5.0,"Dose Limit", "The doseage above-which cases should be analyzed")
    DATE_RANGE_START = inquiry.get_standard_parameter("DATE_RANGE_START")
    DATE_RANGE_END = inquiry.get_standard_parameter("DATE_RANGE_END")


    def run(self, procs, context, extra_procs):
            high_cases = {}
            for proc in procs:
                total_dose = sum([e.Dose_RP for e in proc.get_events()])
                if  total_dose > self.LIMIT.value:
                    high_cases[proc] = {'total dose' : total_dose}

            for proc in high_cases.keys():
                high_cases[proc]['acquisition dose'] = sum([e.Dose_RP for e in proc.get_events() if e.Irradiation_Event_Type =='Stationary Acquisition'])
                high_cases[proc]['spot dose'] = sum([e.Dose_RP for e in proc.get_events() if e.Acquisition_Protocol=='Single'])
                high_cases[proc]['fluoro dose'] = sum([e.Dose_RP for e in proc.get_fluoro_events()])
                high_cases[proc]['acquisition frames'] = sum([e.Number_of_Pulses for e in proc.get_events() if e.Irradiation_Event_Type =='Stationary Acquisition'])
                high_cases[proc]['spot frames'] = sum([e.Number_of_Pulese for e in proc.get_events() if e.Acquisition_Protocol=='Single'])
                high_cases[proc]['fluoro frames'] = sum([e.Number_of_Pulses for e in proc.get_fluoro_events()])
                high_cases[proc]['total frames'] = sum([e.Number_of_Pulses for e in proc.get_events()])
            self.high_cases = high_cases

            
    def get_text(self):
        if len(self.high_cases) == 0:
            return "No cases exceeding the dose limit found in the specified date range."
        else:
            return ''

    def get_figures(self):
        hc = self.high_cases
        figs = []

        pies = []
        for proc in hc.keys():
            # Pie chart of dosages by modality
            fig = plt.figure()
            plt.title("Dose (Gy) By Modality Patient " + str(proc.PatientID) + " on " + str(proc.StudyDate))
            def my_autopct(pct):
                total=hc[proc]['total dose']
                val=pct*total/100.0
                return '{p:.2f}%  ({v:.3f} Gy)'.format(p=pct,v=val)
            plt.pie((hc[proc]['acquisition dose'],
                     hc[proc]['spot dose'],
                     hc[proc]['fluoro dose']),
                    labels = ('acquisition dose','spot dose','fluoro dose'),
                    autopct = my_autopct)
            figs.append(fig)
            # Pie chart of frame counts by modality
            fig = plt.figure()
            plt.title("Frame Count by Modality for Patient " + str(proc.PatientID) + " on " + str(proc.StudyDate))
            def my_autopct(pct):
                total=hc[proc]['total frames']
                val=pct*total/100.0
                return '{p:.2f}%  ({v:.0f})'.format(p=pct,v=val)
            plt.pie((hc[proc]['acquisition frames'],
                     hc[proc]['spot frames'],
                     hc[proc]['fluoro frames']),
                    labels = ('acquisition','spot','fluoro'),
                    autopct = my_autopct)
            figs.append(fig)
            # dose/frame accumulation plot
            figs.append(get_accumulation_fig(proc))
        return figs
        
                
            

            
    
