from srqi.core import inquiry
import matplotlib.pyplot as plt
import numpy as np

def get_accumulation_fig(proc):
    fig = plt.figure()
    plt.title("Accumulation During Procedure for Patient " + str(proc.PatientID) + " on " + str(proc.StudyDate))
    event_starts = [e.DateTime_Started for e in proc.get_events()]   
    # plot doses
    dose_ax = plt.subplot(311)
    dose_ax.plot(event_starts,
                 np.cumsum([e.Dose_RP for e in proc.get_events()])
                 )
    plt.ylabel('Dose (Gy)')
    # plot frames
    frames_ax = plt.subplot(312, sharex = dose_ax)
    frames_ax.plot(event_starts,
                   np.cumsum([e.Number_of_Pulses for e in proc.get_events()])
                   )
    plt.ylabel('# of Frames')
    # plot mag
    mag_ax = plt.subplot(313, sharex = dose_ax)
    mag_ax.plot(event_starts,
                [e.iiDiameter for e in proc.get_events()])
    plt.ylim((200,500))
    plt.ylabel('iiDiameter')
    # plot the event type on top of the mag plot
    a_events = [e for e in proc.get_events() if e.Irradiation_Event_Type =='Stationary Acquisition']
    s_events= [e for e in proc.get_events() if e.Acquisition_Protocol=='Spot']
    f_events = [e for e in proc.get_fluoro_events()]
    o_events = [e for e in proc.get_events() if not (e.Irradiation_Event_Type=="Stationary Acquisition" or e.Acquisition_Protocol=="Spot" or e.Irradiation_Event_Type=="Fluoroscopy")]
    if len(f_events)>0:
        plt.scatter([e.DateTime_Started for e in f_events],
                    [e.iiDiameter for e in f_events],
                    marker='+', c='blue')
    if len(a_events)>0:
        collection = plt.scatter([e.DateTime_Started for e in a_events],
                    [e.iiDiameter for e in a_events],
                    marker='o', c='red')
        collection.set_edgecolor('red')
    if len(s_events)>0:
        collection = plt.scatter([e.DateTime_Started for e in s_events],
                    [e.iiDiameter for e in s_events],
                    marker='o', c='yellow')
        collection.set_edgecolor('yellow')
    if len(o_events)>0:
        collection = plt.scatter([e.DateTime_Started for e in o_events],
                    [e.iiDiameter for e in o_events],
                    marker='o', c='cyan')
        collection.set_edgecolor('cyan')
    # format xlabels
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
                high_cases[proc]['spot dose'] = sum([e.Dose_RP for e in proc.get_events() if e.Acquisition_Protocol=='Spot'])
                high_cases[proc]['fluoro dose'] = sum([e.Dose_RP for e in proc.get_fluoro_events()])
                high_cases[proc]['acquisition frames'] = sum([e.Number_of_Pulses for e in proc.get_events() if e.Irradiation_Event_Type =='Stationary Acquisition'])
                high_cases[proc]['spot frames'] = sum([e.Number_of_Pulses for e in proc.get_events() if e.Acquisition_Protocol=='Spot'])
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
                     hc[proc]['fluoro dose'],
                     hc[proc]['total dose'] - (hc[proc]['spot dose'] + hc[proc]['acquisition dose'] + hc[proc]['fluoro dose'])),
                    labels = ('acquisition','spot','fluoro ', 'other'),
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
                     hc[proc]['fluoro frames'],
                     hc[proc]['total frames'] - (hc[proc]['spot frames'] + hc[proc]['acquisition frames'] + hc[proc]['fluoro frames'])),
                    labels = ('acquisition','spot','fluoro', 'other'),
                    autopct = my_autopct)
            figs.append(fig)
            # dose/frame accumulation plot
            figs.append(get_accumulation_fig(proc))
        return figs
        
                
    def get_tables(self):
        out = []
        hc = self.high_cases
        for proc in self.high_cases.keys():
            heading = ["Patient " + str(proc.PatientID) + " on " + str(proc.StudyDate),
                       'fluoro','acqusition','spot', 'other','total']
            doses = ['Dose (Gy)', hc[proc]['fluoro dose'],
                     hc[proc]['acquisition dose'],
                     hc[proc]['spot dose'],
                     hc[proc]['total dose'] - hc[proc]['acquisition dose'] - hc[proc]['spot dose'] - hc[proc]['fluoro dose'],
                     hc[proc]['total dose']]
            frames = ['Frame Count', hc[proc]['fluoro frames'],
                      hc[proc]['acquisition frames'],
                      hc[proc]['spot frames'],
                      hc[proc]['total frames'] - hc[proc]['spot frames'] - hc[proc]['acquisition frames'] - hc[proc]['fluoro frames'],
                      hc[proc]['total frames']
                      ]
            out.append([heading, doses, frames])
        return out
        

            
    
