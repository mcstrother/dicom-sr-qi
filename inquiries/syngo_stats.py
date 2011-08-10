from srqi.core import inquiry
from srqi.core import Parse_Syngo
from datetime import date
import matplotlib.pyplot as plt

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
        

    def get_figures(self):
        return (self.count_fig,)

    def get_tables(self):
        count_table = [("Period End",
                        "Number of Procedures",
                        "Procedures with Recorded Fluoro Time")] +\
                        zip(self.bin_edges[1:], self.counts, self.with_fluoro_counts)
        return (count_table,)
        

