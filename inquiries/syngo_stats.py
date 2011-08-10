from srqi.core import inquiry
from srqi.core import Parse_Syngo
from datetime import date

class Syngo_Stats(inquiry.Inquiry):
    date_bins = inquiry.Inquiry_Parameter(50, "Number of date bins")
    description = """A simple inquiry for some basic descriptions of
    the amount of Syngo data present in a data set.
    """

    def run(self, procs, context, extra_procs):
        sprocs = [p.get_syngo() for p in procs if p.has_syng()]
        sprocs += [e for e in extra_procs if isinstance(e, Parse_Syngo.Syngo)]
        self.sprocs = sprocs
        self.counts, self.bin_edges, self.count_fig = self.get_count_fig()

    

    def get_count_fig(self):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        counts, bin_edges, _ = plt.hist([p.dos_start.toordinal() for p in self.sprocs],
                           bins=self.date_bins.value)
        bin_edges = [date.fromordinal(int(e)) for e in bin_edges]
        fig = plt.figure()
        plt.scatter(bin_edges[1:], counts)
        fig.autofmt_xdate()
        return (counts, bin_edges, fig)

    def get_figures(self):
        return (self.count_fig,)

    def get_tables(self):
        count_table = [("Period End", "Number of Procedures")] + zip(self.bin_edges[1:], self.counts)
        return (count_table,)
        

