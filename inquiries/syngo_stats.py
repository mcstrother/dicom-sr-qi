from srqi.core import inquiry
from srqi.core import Parse_Syngo, my_utils
from datetime import date
import matplotlib.pyplot as plt
from scipy.stats import anderson
import math

def get_count_fig(date_bins, sprocs, sprocs_with_fluoro):    
    fig = plt.figure()
    counts, bin_edges, _ = plt.hist([p.dos_start.toordinal() for p in sprocs],
                       bins=date_bins.value)
    bin_edges = [date.fromordinal(int(e)) for e in bin_edges]
    with_fluoro_counts , _ , _ = plt.hist([p.dos_start.toordinal() for p in sprocs_with_fluoro],
                       bins=date_bins.value)
    fig = plt.figure()
    plt.scatter(bin_edges[1:], counts, c='r')
    plt.scatter(bin_edges[1:], with_fluoro_counts, c='b')
    fig.autofmt_xdate()
    return (counts, with_fluoro_counts, bin_edges, fig)
    

class Syngo_Stats(inquiry.Inquiry):
    date_bins = inquiry.Inquiry_Parameter(50, "Number of date bins")
    description = """A simple inquiry for some basic descriptions of
    the amount of Syngo data present in a data set.
    """

    def run(self, procs, context, extra_procs):
        sprocs = [p.get_syngo() for p in procs if p.has_syngo()]
        sprocs += [e for e in extra_procs if isinstance(e, Parse_Syngo.Syngo)]
        self.sprocs = sprocs
        sprocs_with_fluoro = [p for p in sprocs if not p.fluoro is None]
        self.counts, self.with_fluoro_counts, self.bin_edges, self.count_fig = get_count_fig(self.date_bins,
                                                                    self.sprocs,
                                                                    sprocs_with_fluoro)    
        self.sprocs_by_cpt = my_utils.organize(sprocs, lambda x:x.get_cpts_as_string())

    def get_figures(self):
        return (self.count_fig,)

    def get_tables(self):
        #count of procedures over time
        count_table = [("Period End",
                        "Number of Procedures",
                        "Procedures with Recorded Fluoro Time")] +\
                        zip(self.bin_edges[1:], self.counts, self.with_fluoro_counts)
        #break down by cpt code
        cpt_table = [("CPT Code Combination","Number of Procedures",
                      "Number of Procedures with Fluoro", "Anderson Value", "Critical Values", "P-values")]
        for cpt, sprocs in self.sprocs_by_cpt.iteritems():
            cpt_table += [['"'+cpt+'"', len(sprocs), len([p for p in sprocs if not p.fluoro is None])]]
            fluoros = [p.fluoro if not p.fluoro ==0 else .5 for p in sprocs if not p.fluoro is None] 
            try:
                fit_statistic = anderson([math.log(float(x)) for x in fluoros],
                                    dist='norm')
            except ZeroDivisionError:
                fit_statistics = None
            cpt_table[-1] += [fit_statistic[0], list(fit_statistic[1]),list(fit_statistic[2])]
        return (count_table, cpt_table)
        

