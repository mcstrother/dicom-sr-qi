import os, sys
#allow imports of standard srqi modules
srqi_containing_dir = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(srqi_containing_dir)
from srqi.core import my_utils
import numpy as np
import math
from datetime import date

SIMULATION = 'july'
#SIMULATION = 'improvement'
JULY_EFFECT = .5
WINDOW_SIZE = 50

def add_new_fellow_factor(proc):
    start_date = p.get_start_date()

def main():
    # get all the Syngo objects
    procs, extra_procs = my_utils.get_procs_from_files(["C:\\Users\\mcstrother\\Documents\\Duncan Research\\srqi\\Data\\BJH\\NEW_____Combined months_IR_Syngo_KAR4_All-Exams.xls"])
    for p in procs:
        if p.has_syngo():
            extra_procs.append(p.get_syngo())
    syngo_procs = [p for p in extra_procs if not p.fluoro is None]
    syngo_procs.sort(key = lambda p:p.get_start_date())
    fake_fluoros = np.random.lognormal(math.log(5), .5, (len(syngo_procs)))
    for i,p in enumerate(syngo_procs):
        p.fluoro = fake_fluoros[i]
    for i,p in enumerate(syngo_procs):
        if p.rad1 == 'SAAD, N.':
            p.rad1 = 'Simulated'
            orig_fluoro =p.fluoro
            if SIMULATION == 'improvement':
                #physician improves 20% over the course of the time period
                p.fluoro = p.fluoro * (1.0 - .2*i/len(syngo_procs))
            elif SIMULATION == 'july':
                july = date(p.get_start_date().year, 7,1)
                days = (p.get_start_date() - july).days #days since july 1
                if days > 0:
                    p.fluoro = p.fluoro * (1 + JULY_EFFECT - JULY_EFFECT * days/182)

    from srqi.inquiries.operator_improvement import Operator_Improvement
    import matplotlib.pyplot as plt
    oi_cls = Operator_Improvement
    oi_cls.PROCS_PER_WINDOW.set_value(WINDOW_SIZE)
    oi = oi_cls([], [], syngo_procs)
    oi.get_figures()
    plt.show()  


if __name__ == '__main__':
    main()
