from mirqi.core import inquiry
from mirqi.inquiries.operator_improvement import get_procedures_helper, sort_by_rads_helper
import collections
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt

class Operator_Improvement_Surface(inquiry.Inquiry):
    MIN_REPS = inquiry.Inquiry_Parameter(50, "Minimum procedure count",
                                         "The minimum number of times a procedure with the same CPT codes must occur to be considered to have a reasonable distribution")
    PROCS_PER_WINDOW = inquiry.Inquiry_Parameter(100, "Procedures Per Window",
                                                 "Number of procedures that should be considered in the sliding window calculation of the operators performance metric.")
    STEP_SIZE = inquiry.Inquiry_Parameter(50, "Step size",
                                          "Number of procedures between the beginnings of each window. ")
    
    def run(self, procs, context, extra_procs):
        cpt_to_procs = get_procedures_helper(procs, extra_procs, self.MIN_REPS.value)
        self.rad1_to_procs = sort_by_rads_helper(sum(cpt_to_procs.values(),[]), self.PROCS_PER_WINDOW.value)
                                          

    def get_figures(self):
        
        ys = [1.0/self.PROCS_PER_WINDOW.value*i for i in range(self.PROCS_PER_WINDOW.value)]
        
        for rad1, procs in self.rad1_to_procs.iteritems():
            verts = [] #need to change things so more than last guy is plotted
            for i in range(0, len(procs), self.STEP_SIZE.value):
                if i+self.STEP_SIZE.value < len(procs):
                    xs = sorted([proc.fluoro for proc in procs[i:i+self.STEP_SIZE.value]])
                    verts.append(zip(xs,ys))
        zs = range(len(verts))
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        poly = PolyCollection(verts,
                              facecolors = [colorConverter.to_rgba('g', alpha=.6) for _ in range(len(verts))])
        poly.set_alpha(0.7)
        ax.add_collection3d(poly, zs=zs, zdir='y')
        plt.show()
        return [fig]

if __name__ == '__main__':
    inquiry.inquiry_main(Operator_Improvement_Surface, 'bjh')
