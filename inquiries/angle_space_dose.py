from srqi.core import inquiry


class Angle_Space_Dose(inquiry.Inquiry):
    DATE_RANGE_START = inquiry.get_standard_parameter("DATE_RANGE_START")
    DATE_RANGE_END = inquiry.get_standard_parameter("DATE_RANGE_END")

    def run(self, sr_procs, context, extra_procs):
        out = [] #out[proc #][event #][0 or 1, primary or secondary angle]
        for p in sr_procs:
            if len(p.get_events())>0:
                p_events = [(e.Positioner_Primary_Angle,
                             e.Positioner_Secondary_Angle, e.Dose_RP) for e in p.get_events()]
                out.append(p_events)
        self.data = out

    def get_figures(self):
        import matplotlib.pyplot as plt
        import numpy as np
        figs = []
        for i,p_events in enumerate(self.data):
            xs,ys, weights = zip(*p_events)
            #copied almost verbatem from http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram2d.html
            H, xedges ,yedges = np.histogram2d(xs,ys, weights = weights)
            extent = [yedges[0], yedges[-1], xedges[-1],xedges[0]]
            fig = plt.figure()
            plt.imshow(H, extent=extent, aspect='auto', interpolation='nearest')
            cb = plt.colorbar()
            cb.set_label("Dose RP (Gy)")
            plt.title("Procedure #" + str(i) + " starting on "+ str(self.DATE_RANGE_START.value))
            plt.xlabel("Primary Angle")
            plt.ylabel("Secondary Angle")
            figs.append(fig)
        return figs
            
            

