from srqi.core import inquiry
from srqi.inquiries.operator_improvement import get_procedures_helper, sort_by_rads_helper, get_procedure_windows
import collections
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import numpy as np




class Operator_Improvement_Surface(inquiry.Inquiry):
    MIN_REPS = inquiry.Inquiry_Parameter(500, "Minimum procedure count",
                                         "The minimum number of times a procedure with the same CPT codes must occur to be considered to have a reasonable distribution")
    PROCS_PER_WINDOW = inquiry.Inquiry_Parameter(400, "Procedures Per Window",
                                                 "Number of procedures that should be considered in the sliding window calculation of the operators performance metric.")
    STEP_SIZE = inquiry.Inquiry_Parameter(400, "Step size",
                                          "Number of procedures between the beginnings of each window. ")
    
    def run(self, procs, context, extra_procs):
        cpt_to_procs = get_procedures_helper(procs, extra_procs, self.MIN_REPS.value)
        self.included_cpts = cpt_to_procs.keys() # just used to print
        self.rad1_to_procs = sort_by_rads_helper(sum(cpt_to_procs.values(),[]), self.PROCS_PER_WINDOW.value)

    def get_figures(self):
        from matplotlib.collections import LineCollection
        figs = []
        ys = [(1.0/self.PROCS_PER_WINDOW.value)*(i+1) for i in range(self.PROCS_PER_WINDOW.value)]
        all_xs = []
        for rad1, procs in self.rad1_to_procs.iteritems():
            windows = get_procedure_windows(procs, self.PROCS_PER_WINDOW.value,
                                   self.STEP_SIZE.value)
            all_xs = []
            for window in windows:
                all_xs.append([p.fluoro for p in window])
            #the matplotlib part
            fig = plt.figure()
            ax = plt.gca()
            ax.set_xlim(0,10)
            ax.set_ylim(0,1)
            line_segments= LineCollection([zip(xs,ys) for xs in all_xs])
            line_segments.set_array(np.array(range(len(all_xs))))
            ax.add_collection(line_segments)
            plt.title(rad1)
            plt.xlabel("Fluoro Time")
            plt.ylabel("Fraction of Procedures Below Fluoro Time")
            colorbar_ax = fig.colorbar(line_segments)#ticks = ?
            colorbar_ax.set_label("Window Number")
            figs.append(fig)
        return figs



    def get_text(self):
        return "This analysis includes procedures with the following cpt codes " + '\n'.join(self.included_cpts)

if __name__ == '__main__':
    inquiry.inquiry_main(Operator_Improvement_Surface, 'bjh')
