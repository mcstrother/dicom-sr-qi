from mirqi.core import inquiry, Parse_Syngo, my_utils
import matplotlib.pyplot as plt
import numpy as np
import collections

def get_procedures_helper(procs, extra_procs, min_reps):
    """Extract all the Syngo procedures that we're interested in
    (i.e. all the ones that have enough repetitions of the same procedure)
    and return them as a dictionary mapping cpt code combinations to
    lists of procedures

    Arguments:
        procs : a list of (SR) Procedure objects
        extra_procs : a list of non-SR procedure objects that could not
            be assigned to SR procedures
    """
    # extract all the syngo procedures from procs and extra_procs
    syngo_procs = [p for p in extra_procs if type(p) == Parse_Syngo.Syngo]
    for proc in procs:
        if proc.has_syngo():
            syngo_procs.append(proc.get_syngo())
    #remove procs without a fluoro number entered
    syngo_procs = [p for p in syngo_procs if not p.fluoro is None]
    #remove procedures with less than MIN_REPS.value instances of same cpt code
    cpt_to_procs = my_utils.organize(syngo_procs, lambda p: p.get_cpts_as_string())
    for k in cpt_to_procs.keys():
        if len(cpt_to_procs[k]) < min_reps:
            del cpt_to_procs[k]
    return cpt_to_procs
    


class Operator_Improvement(inquiry.Inquiry):
    MIN_REPS = inquiry.Inquiry_Parameter(50, "Minimum procedure count",
                                         "The minimum number of times a procedure with the same CPT codes must occur to be considered to have a reasonable distribution")
    PROCS_PER_WINDOW = inquiry.Inquiry_Parameter(50, "Procedures Per Window",
                                                 "Number of procedures that should be considered in the sliding window calculation of the operators performance metric.")
    def run(self, procs, context, extra_procs):
        cpt_to_procs = get_procedures_helper(procs, extra_procs, self.MIN_REPS.value)
        # calculate statistics for each procedure type
        medians = {}
        std_devs = {}
        means = {}
        for cpt, p_list in cpt_to_procs.iteritems():
            fluoro_list = [p.fluoro for p in p_list]
            medians[cpt] = float(np.median(fluoro_list))
            std_devs[cpt] = np.std(fluoro_list)
            means[cpt] = np.mean(fluoro_list)
        # organize by rad1 and sort by date
        rad1_to_procs = my_utils.organize(sum(cpt_to_procs.values(),[]), lambda p:p.rad1)
        for p_list in rad1_to_procs.values():
            p_list.sort(key = lambda p:p.dos_start)
        # remove rads with too few procedures
        for rad1 in rad1_to_procs.keys():
            if len(rad1_to_procs[rad1]) < (self.PROCS_PER_WINDOW.value +2):#have to be able to plot at least 3 points
                del rad1_to_procs[rad1]
        self._the_meat(rad1_to_procs, medians)

    
    def _the_meat(self, rad1_to_procs, medians):
        """Set self.lookup, which is the meat of self.run
        Everything else in self.run is basically preprocessing

        Arguments:
            rad1_to_procs : dictionary mapping rad1 (a string) to a list of
                Syngo procedures
            medians : dictionary mapping a cpt code set (a string) to a float
        """
        # calculate metrics
        rad1_to_out = {}
        for rad1, p_list in rad1_to_procs.iteritems():
            out = []
            metric_queue = collections.deque()
            cum_metric = 0
            for i, proc in enumerate(p_list):
                fluoro = float(proc.fluoro)
                med = medians[proc.get_cpts_as_string()]
                metric =(fluoro-med)#/std_dev
                cum_metric += metric
                metric_queue.append(metric)
                if len(metric_queue)>=self.PROCS_PER_WINDOW.value:
                    if len(metric_queue) > self.PROCS_PER_WINDOW.value:
                        cum_metric -= metric_queue.popleft()
                    if i == len(p_list)-1 or not (proc.dos_start == p_list[i+1].dos_start):
                        out.append((proc.dos_start, cum_metric))
            rad1_to_out[rad1] = out
        self.lookup = rad1_to_out #rad1_to_out[rad1][window_number] = (date, metric value)
        
    """
    def get_tables(self):
        out = []
        for proc in self.syngo_procs:
            if hasattr(proc, 'fluoro'):
                out.append([proc.fluoro])
            else:
                out.append([None])
        return out
    """
    def get_figures(self):
        figs = []
        for rad1 in self.lookup.keys():
            dates, metrics = zip(*self.lookup[rad1]) #pythonic idiom for "unzip"
            fig = plt.figure()
            plt.plot(dates, metrics)
            plt.title(rad1)
            plt.xlabel("Window End Date")
            plt.ylabel("Metric (positive values --> higher fluoro time)")
            fig.autofmt_xdate()
            figs.append(fig)
        #all together
        fig = plt.figure()
        for rad1 in self.lookup.keys():
            dates, metrics = zip(*self.lookup[rad1]) #pythonic idiom for "unzip"
            plt.plot(dates, metrics)
            plt.title("All combined")
            plt.xlabel("Window End Date")
            plt.ylabel("Metric (positive values --> higher fluoro time)")
            fig.autofmt_xdate()
        figs.append(fig)
        #all averaged together
        
        return figs

        
if __name__ == '__main__':
    inquiry.inquiry_main(Operator_Improvement, 'bjh')

