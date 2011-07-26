import os, sys
#allow imports of standard srqi modules
srqi_containing_dir = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(srqi_containing_dir)

from srqi.core import my_utils
import heapq
import numpy as np
import random

NUM_CPTS = 3
   
def get_improvement_pattern(most_rad1, least_rad1, common_cpts, simulate_procs):
    """
    Parameters:
        most_rad1 - string of the cpt code of the rad1 that uses the most fluoro
            on average
        least_rad1 - string of the cpt code of the rad1 that uses the least
            fluoro on average
        common_cpts - a dictionary of dictionaries.
            common_cpts[cpt_string][rad1] -> list of Syngo objects
        simulate_procs - a list of procedures which we will use as a basis
            for the simulated procedures. we will just replace the fluoro times
            of these procedures in order to generate the simulated procs

    Returns:
        None. Just modifies the procedures in simulate_procs
    """
    total_procs = len(simulate_procs)
    simulate_procs.sort(key = lambda p: p.get_start_date())
    for i,proc in enumerate(simulate_procs):
        proc.rad1 = "Simulant"
        cpt = proc.get_cpts_as_string()
        prob = float(i)/total_procs
        rand = random.random()
        # choose which pool of procedures to draw from according to the
        # random number. over time the chances of drawing from the pool that
        # uses less fluoro increases
        if rand > prob:
            if i % 100 ==0:
                print ("Most", rand, prob)
            proc.fluoro = random.choice(common_cpts[cpt][most_rad1]).fluoro
        else:
            if i % 100 == 0:
                print ("Least", rand, prob)
            proc.fluoro = random.choice(common_cpts[cpt][least_rad1]).fluoro
    
def simulate_from_real_data(simulate_procs, syngo_procs):
    # get the most common cpt codes as common_cpts[cpt_string] -> list of Syngo objects
    sprocs_by_cpt = my_utils.organize(syngo_procs, lambda p:p.get_cpts_as_string())
    common_cpts = heapq.nlargest(NUM_CPTS,
                                 sprocs_by_cpt.iteritems(),
                                 key =lambda x:len(x[1]))
    #most_common_cpt = common_cpts[0][0]
    common_cpts = dict(common_cpts)
    # now make common_cpts[cpt_string][rad1] -> list of Syngo objects
    for k in common_cpts.keys():
        common_cpts[k] = my_utils.organize(common_cpts[k], lambda p:p.rad1)
    # find the physician who use the most and least fluoro on average in the
    # most common procedure
    least_rad1 = "PICUS, D."
    #least_rad1 = min(common_cpts[most_common_cpt].keys(),
    #    key = lambda rad1: np.mean([p.fluoro for p in common_cpts[most_common_cpt][rad1]]))
    # take the second most, since the most hasn't done any of some common procedures
    #_, most_rad1 = heapq.nlargest(2,common_cpts[most_common_cpt].keys(),
    #    key = lambda rad1: np.mean([p.fluoro for p in common_cpts[most_common_cpt][rad1]]))
    most_rad1 = "SAAD, N."
    simulate_procs = [p for p in simulate_procs if p.get_cpts_as_string() in common_cpts]
    get_improvement_pattern(most_rad1, least_rad1, common_cpts, simulate_procs)
    most_rad1_procs = [p for p in syngo_procs if p.get_cpts_as_string() in common_cpts and p.rad1 == most_rad1]
    least_rad1_procs = [p for p in syngo_procs if p.get_cpts_as_string() in common_cpts and p.rad1 == least_rad1]
    return simulate_procs, most_rad1_procs, least_rad1_procs

def main():
    # get all the Syngo objects
    procs, extra_procs = my_utils.get_procs_from_files(["C:\\Users\\mcstrother\\Documents\\Duncan Research\\srqi\\Data\\BJH\\NEW_____Combined months_IR_Syngo_KAR4_All-Exams.xls"])
    for p in procs:
        if p.has_syngo():
            extra_procs.append(p.get_syngo())
    syngo_procs = [p for p in extra_procs if not p.fluoro is None]
    simulate_procs = [p for p in syngo_procs if p.rad1 == 'KIM, S.']
    # manipulate the procedures
    simulate_procs, most_rad1_procs, least_rad1_procs = simulate_from_real_data(simulate_procs,
                                                                                syngo_procs)
    # plot results
    from srqi.inquiries.operator_improvement import Operator_Improvement
    import matplotlib.pyplot as plt
    oi_cls = Operator_Improvement
    oi_cls.MIN_REPS.set_value(1)
    oi = oi_cls([], [], simulate_procs + most_rad1_procs + least_rad1_procs)
    oi.get_figures()
    plt.show()
    

if __name__ == '__main__':
    main()



