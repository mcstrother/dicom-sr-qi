from srqi.core import inquiry



class Sid_Freq(inquiry.Inquiry):
    DATE_RANGE_START = inquiry.get_standard_parameter("DATE_RANGE_START")
    DATE_RANGE_END = inquiry.get_standard_parameter("DATE_RANGE_END")


    def run(self, sr_procs, context, extra_procs):
        events = []
        for p in sr_procs:
            events = p.get_events()
        self.sids = [e.Distance_Source_to_Detector for e in events]

    def get_figures(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.hist(self.sids)
        plt.xlabel("SID")
        plt.ylabel("Irradiation Event Count")
        plt.title("Frequency of SID Values in Irradiation Events")
        return [fig]
        
    

