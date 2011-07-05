from mirqi.core import inquiry, Parse_Syngo, my_utils
import matplotlib.pyplot as plt
import heapq


class CPT_Box_Plots(inquiry.Inquiry):
    NUM_PROCEDURE_TYPES = inquiry.Inquiry_Parameter(5, "Number of Procedure Types",
                                                    "The Maximum number of procedure types (as defined by CPT code combinations) to be plotted")

    def run(self, procs, context, extra_procs):
        #extract all syngo procs with fluoro values recorded
        syngo_procs = [p for p in extra_procs if type(p) == Parse_Syngo.Syngo]
        for proc in procs:
            if proc.has_syngo():
                syngo_procs.append(proc.get_syngo())
        syngo_procs = [p for p in syngo_procs if not p.fluoro is None]
        #get the fluoro times of the 5 most common cpt code combos
        cpts_to_procs = my_utils.organize(syngo_procs, lambda x: x.get_cpts_as_string())
        common_cpts = heapq.nlargest(self.NUM_PROCEDURE_TYPES.value,
                       cpts_to_procs.keys(),
                       key = lambda k: len(cpts_to_procs[k]))
        cpts_to_fluoros = {}
        for cpt in common_cpts:
            cpts_to_fluoros[cpt] = [p.fluoro for p in cpts_to_procs[cpt]]
        self.lookup = cpts_to_fluoros

    def get_figure(self):
        fig = plt.figure()
        plt.boxplot(self.lookup.values())
        return fig


    def get_table(self):
        out = []
        for cpt, f_list in self.lookup.iteritems():
            out.append([cpt] + sorted(f_list))
        return out
        
                
        
if __name__ == '__main__':
    inquiry.inquiry_main(CPT_Box_Plots,'slch')


