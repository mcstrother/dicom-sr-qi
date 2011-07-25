from srqi.core import inquiry, Parse_Syngo, my_utils
import matplotlib.pyplot as plt
import heapq
import math

class Cpt_Box_Plots(inquiry.Inquiry):
    NUM_PROCEDURE_TYPES = inquiry.Inquiry_Parameter(5, "Number of Procedure Types",
                                                    "The Maximum number of procedure types (as defined by CPT code combinations) to be plotted")
    description = """Creates box plots for fluoro times of the most common CPT code combinations

    Data requires:
        Syngo
    """
    USE_LOG = inquiry.Inquiry_Parameter(True, "Plot log of fluoro times?",
                                        "Fluoro times tend to be lognormally distributed. Procedures with 0 fluoro time will be ignored.")
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
            if not self.USE_LOG.value:
                cpts_to_fluoros[cpt] = [p.fluoro for p in cpts_to_procs[cpt]]
            else:
                log_fluoros = []
                for p in cpts_to_procs[cpt]:
                    try:
                        log_fluoros.append(math.log(p.fluoro))
                    except ValueError:
                        pass #ignore procedures with 0 fluoro time
                cpts_to_fluoros[cpt] = log_fluoros
        self.lookup = cpts_to_fluoros

    def get_figures(self):
        fig = plt.figure()
        plt.title("Fluoro Times for Most Common Procedures at BJH")
        plt.xlabel("Procedure CPT codes")
        plt.ylabel("Fluoro time (seconds)")
        widths = [len(v) for v in self.lookup.values()]
        average_width = sum(widths)/len(widths)
        widths = [float(x)/average_width *.5 for x in widths]
        plt.boxplot(self.lookup.values(),
                     widths = widths)
        labels = self.lookup.keys()
        for cpt in labels:
            cpt.replace(',','\n')
        plt.gca().set_xticklabels(self.lookup.keys(), size ='x-small')
        #plt.setp(plt.gca(), 'xticklabels',self.lookup.keys())
        return [fig]


    def get_tables(self):
        out = []
        for cpt, f_list in self.lookup.iteritems():
            out.append([cpt] + sorted(f_list))
        return [out]

    def get_text(self):
        return "Note: widths on the box plots represent the number of procedures with the given CPT code"
                
        
if __name__ == '__main__':
    inquiry.inquiry_main(CPT_Box_Plots,'slch')


