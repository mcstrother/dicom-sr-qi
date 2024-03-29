from srqi.core import inquiry, Parse_Syngo, my_utils
import matplotlib.pyplot as plt
import numpy as np
import collections
import math


def get_procedures_helper(procs, extra_procs, min_reps):
    """Extract all the Syngo procedures that we're interested in
    (i.e. all the ones that have enough repetitions of the same procedure)
    and return them as a dictionary mapping cpt code combinations to
    lists of procedures

    Arguments:
        procs : a list of (SR) Procedure objects
        extra_procs : a list of non-SR procedure objects that could not
            be assigned to SR procedures

    Returns:
        a dictionary mapping cpt codes (represented as strings) to lists of
            Syngo objects
    """
    # extract all the syngo procedures from procs and extra_procs
    syngo_procs = [p for p in extra_procs if type(p) == Parse_Syngo.Syngo]
    for proc in procs:
        if proc.has_syngo():
            proc.get_syngo().fluoro = my_utils.total_seconds(proc.get_pedal_time())/60.0
            syngo_procs.append(proc.get_syngo())
    #remove procs without a fluoro time entered
    syngo_procs = [p for p in syngo_procs if not p.fluoro is None]
    #remove procedures with less than MIN_REPS.value instances of same cpt code
    cpt_to_procs = my_utils.organize(syngo_procs, lambda p: p.get_cpts_as_string())
    for k in cpt_to_procs.keys():
        if len(cpt_to_procs[k]) < min_reps:
            del cpt_to_procs[k]
    #remove procedures where there is no variation
    for k in cpt_to_procs.keys():
        remove = True
        procs = cpt_to_procs[k]
        for i in range(1,len(cpt_to_procs[k])):
            if not procs[i] == procs[0]:
                remove = False
                break
        if remove:
            del cpt_to_procs[k]
    return cpt_to_procs
    
def sort_by_rads_helper(procs, procs_per_window):
    """
    Arguments:
        procs : iterable of Syngo objects
        procs_per_window :

    Returns:
        a dict, rad1_to_procs[rad1]-->list of procedures sorted by dos_start
    """
    rad1_to_procs = my_utils.organize(procs, lambda p:p.rad1)
    # sort each radiologist's list of procedures by their start date
    for p_list in rad1_to_procs.values():
        p_list.sort(key = lambda p:p.dos_start)
    # remove rads with too few procedures
    for rad1 in rad1_to_procs.keys():
        if len(rad1_to_procs[rad1]) < (procs_per_window +2):#have to be able to plot at least 3 points
            del rad1_to_procs[rad1]
    return rad1_to_procs


def get_procedure_windows(procs, procs_per_window, step_size ):
    """
    Parameters:
        procedures : an iterable of Syngo objects
        procs_per_window : an int
    Returns:
        a list of lists of Syngo objects, each representing a window and
            having len of procs_per_window. each list is sorted by the
            procedure fluoro time
    """
    windows = []
    for i in range(0, len(procs), step_size):
        if i+procs_per_window <= len(procs):
            window = sorted(procs[i:i+procs_per_window],
                            key = lambda x:x.fluoro)
            windows.append(window)
    return windows

def _get_metric(proc, medians, normalize_penalty, clamp,
                use_log, log_fluoros, log_means, log_devs):
    fluoro = float(proc.fluoro)
    if use_log.value:
        log_mean = log_means[proc.get_cpts_as_string()]
        log_dev = log_devs[proc.get_cpts_as_string()]
        metric = (fluoro-log_mean)/log_dev
        if metric > 2 and clamp.value: # clamp at 2 std devs
            metric = 2
    else:
        med = medians[proc.get_cpts_as_string()]
        metric =(fluoro-med)
        if med >0 and normalize_penalty.value:
            metric = metric/float(med)
            if metric > 1 and clamp.value:#clamp at 2x median value
                metric = 1
        if metric > med and clamp.value:
            metric = med#clamp at 2x median value
    return metric

class Operator_Improvement(inquiry.Inquiry):
    MIN_REPS = inquiry.Inquiry_Parameter(500, "Minimum procedure count",
                                         "The minimum number of times a procedure with the same CPT codes must occur to be considered to have a reasonable distribution")
    PROCS_PER_WINDOW = inquiry.Inquiry_Parameter(400, "Procedures Per Window",
                                                 "Number of procedures that should be considered in the sliding window calculation of the operators performance metric.")
    CLAMP = inquiry.Inquiry_Parameter(True, "Limit penalty to 2x median",
                                      "If an operator exceeds the median fluoro time on a given procedure by more than 2x the median, only penalize him by 1x the median.")
    NORMALIZE_PENALTY = inquiry.Inquiry_Parameter(True, "Normalize penalties",
                                                  "Divide penalties by the median to account for greater variation in longer procedures.")
    USE_LOG = inquiry.Inquiry_Parameter(True, "Use Lognormal Z-score")
                                        
    def run(self, procs, context, extra_procs):
        cpt_to_procs = get_procedures_helper(procs, extra_procs, self.MIN_REPS.value)
        # calculate statistics for each procedure type
        medians = {}
        std_devs = {}
        means = {}
        log_fluoros = {}
        log_means  = {}
        log_devs = {}
        for cpt, p_list in cpt_to_procs.iteritems():
            fluoro_list = [p.fluoro for p in p_list]
            medians[cpt] = float(np.median(fluoro_list))
            std_devs[cpt] = np.std(fluoro_list)
            means[cpt] = np.mean(fluoro_list)
            log_fluoros[cpt] = [math.log(x) if not x ==0 else math.log(.5) for x in fluoro_list]
            log_means[cpt] = np.mean(log_fluoros[cpt])#default to .5 since that is the lowest number that won't be rounded down to 0
            log_devs[cpt] = np.std(log_fluoros[cpt])
        # organize by rad1 and sort by date
        rad1_to_procs = sort_by_rads_helper( sum(cpt_to_procs.values(),[]), self.PROCS_PER_WINDOW.value )
        self._the_meat(rad1_to_procs, medians, log_fluoros, log_means, log_devs)
        self.medians = medians
    
    def _the_meat(self, rad1_to_procs, medians, log_fluoros, log_means, log_devs):
        """Set self.lookup, which is the meat of self.run
        Everything else in self.run is basically preprocessing

        Arguments:
            rad1_to_procs : dictionary mapping rad1 (a string) to a list of
                Syngo procedures
            medians : dictionary mapping a cpt code set (a string) to a float
        """
        # calculate raw deviations
        raw_devs = {}
        for rad1, p_list in rad1_to_procs.iteritems():
            devs = []
            for p in p_list:
                med = medians[p.get_cpts_as_string()]
                devs.append(p.fluoro-med)
            raw_devs[rad1] = devs
        self.raw_devs = raw_devs
        # calculate metrics
        rad1_to_out = {}
        for rad1, p_list in rad1_to_procs.iteritems():
            out = []
            metric_queue = collections.deque()
            cum_metric = 0
            for i, proc in enumerate(p_list):
                
                metric = _get_metric(proc, medians = medians,
                                     normalize_penalty = self.NORMALIZE_PENALTY,
                                     clamp = self.CLAMP,
                                     use_log = self.USE_LOG,
                                     log_fluoros = log_fluoros,
                                     log_means = log_means,
                                     log_devs = log_devs)
                cum_metric += metric
                metric_queue.append(metric)
                if len(metric_queue)>=self.PROCS_PER_WINDOW.value:
                    if len(metric_queue) > self.PROCS_PER_WINDOW.value:
                        cum_metric -= metric_queue.popleft()
                    if i == len(p_list)-1 or not (proc.dos_start == p_list[i+1].dos_start):
                        out.append((proc.dos_start, cum_metric/self.PROCS_PER_WINDOW.value))
            rad1_to_out[rad1] = out
        self.lookup = rad1_to_out #rad1_to_out[rad1][window_number] = (date, metric value)


    def get_tables(self):
        out = []
        for rad1 in self.lookup.keys():
            dates, metrics = zip(*self.lookup[rad1])
            dates = [''] + list(dates)
            metrics = [rad1] + list(metrics)
            out.append((dates,metrics))
        medians_table = [("Procedure Type", "Median Fluoro Time")]
        for cpts, median in self.medians.iteritems():
            medians_table.append((cpts, median))
        out.append(medians_table)
        return out

    def _get_all_together_figure(self, legend = False):
        fig = plt.figure()
        from matplotlib import cm
        colormap = cm.get_cmap(name='hsv')
        colors = [colormap(i) for i in np.linspace(0,0.9, len(self.lookup.keys()))]
        for i,rad1 in enumerate(self.lookup.keys()):
            dates, metrics = zip(*self.lookup[rad1]) #pythonic idiom for "unzip"
            plt.plot(dates, metrics, color = colors[i], label =rad1)
        plt.title("All combined")
        plt.xlabel("Window End Date")
        plt.ylabel("Metric (positive values --> higher fluoro time)")
        fig.autofmt_xdate()
        if legend:
            plt.legend()
        return fig
        
   
    def get_figures(self):
        figs = []
        #all together
        figs.append(self._get_all_together_figure(False))
        figs.append(self._get_all_together_figure(True))
        axis_ranges = plt.axis()
        #individual operators
        for rad1 in self.lookup.keys():
            dates, metrics = zip(*self.lookup[rad1]) #pythonic idiom for "unzip"
            fig = plt.figure()
            plt.plot(dates, metrics)
            plt.axis(axis_ranges)
            plt.title(rad1)
            plt.xlabel("Window End Date")
            plt.ylabel("Metric (positive values --> higher fluoro time)")
            fig.autofmt_xdate()
            figs.append(fig)
        
        #TODO: all averaged together
        
        return figs

        
if __name__ == '__main__':
    inquiry.inquiry_main(Operator_Improvement, 'bjh')

