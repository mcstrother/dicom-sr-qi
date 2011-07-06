from mirqi.core import inquiry, Parse_Syngo, my_utils
import matplotlib.pyplot as plt
import numpy as np
import collections

class Operator_Improvement(inquiry.Inquiry):
    MIN_REPS = inquiry.Inquiry_Parameter(8, "Minimum procedure count",
                                         "The minimum number of times a procedure with the same CPT codes must occur to be considered to have a reasonable distribution")
    PROCS_PER_WINDOW = inquiry.Inquiry_Parameter(20, "Procedures Per Window",
                                                 "Number of procedures that should be considered in the sliding window calculation of the operators performance metric.")

    def run(self, procs, context, extra_procs):
        # extract all the syngo procedures from procs and extra_procs
        #
        syngo_procs = [p for p in extra_procs if type(p) == Parse_Syngo.Syngo]
        for proc in procs:
            if proc.has_syngo():
                syngo_procs.append(proc.get_syngo())
        cpt_to_procs = my_utils.organize(syngo_procs, lambda p: p.get_cpts_as_string())
        #remove procedures with less than MIN_REPS.value instances of same cpt code
        to_remove = []
        for k, v in cpt_to_procs.iteritems():
            if len(v) < self.MIN_REPS.value:
                to_remove.append(k)
        for cpt in to_remove:
            del cpt_to_procs[cpt]
        # calculate statistics for each procedure type
        medians = {}
        std_devs = {}
        for cpt, p_list in cpt_to_procs.iteritems():
            fluoro_list = [p.fluoro for p in p_list]
            medians[cpt] = np.median(fluoro_list)
            std_devs[cpt] = np.std(fluoro_list)
        # organize by rad1 and sort by date
        rad1_to_procs = my_utils.organize(sum(cpt_to_procs.values(),[]), lambda p:p.rad1)
        for p_list in rad1_to_procs:
            p_list.sort(key = lambda p:p.dos_start)
        # calculate metrics
        rad1_to_out = {}
        for rad1, p_list in rad1_to_procs:
            if len(p_list) < self.PROCS_PER_WINDOW.value:
                print "Skipping " + rad1 + " due to lack of procedures."
            out = []
            metric_queue = collections.deque()
            for i in range(len(p_list)):
                fluoro = float(p_list[i].fluoro)
                med = medians[p_list[i].get_cpts_as_string()]
                std_dev = std_devs[p_list[i].get_cpts_as_string()]
                metric = (fluoro-med)/std_dev
                cum_metric += metric
                metric_queue.append(metric)
                if i >= self.PROCS_PER_WINDOW-1:
                    cum_metric -= metric_list.popleft()
                    if i == len(p_list-1) or not p_list[i].dos_start == p_list[i+1].dos_start:
                        out.append((p_list[i].dos_start,cum_metric))
            rad1_to_out[rad1] = out
        self.lookup = rad1_to_out #rad1_to_out[rad1][window_number] = (date, metric value)
            

    def get_table(self):
        out = []
        for proc in self.syngo_procs:
            if hasattr(proc, 'fluoro'):
                out.append([proc.fluoro])
            else:
                out.append([None])
        return out

    def get_figure(self):
        fig = plt.figure()
        return fig

        


