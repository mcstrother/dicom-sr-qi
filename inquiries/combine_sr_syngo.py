from srqi.core import inquiry

class Combine_Sr_Syngo(inquiry.Inquiry):


    def run(self, sr_procs, context, extra_procs):
        self.sr_procs = sr_procs

    def get_tables(self):
        #get the standard heading list except for the last entry, which is 'CPTs'
        headings = self.sr_procs[0].get_syngo().get_heading_list()[:-1]
        headings += ["Total Dose (Gy) (SR)", "Total DAP (Gym2) (SR)", "Pedal Time (s) (SR)"]
        headings += ["CPTs"]
        table = [headings]
        for sr_proc in self.sr_procs:
            # init row with all data from Syngo except CPTs
            row = []
            syngo = sr_proc.get_syngo()
            row += syngo.get_data_list()[:-1]
            #get the data we need from SR
            total_Dose = sr_proc.get_total_Dose()
            total_DAP = sr_proc.get_total_DAP()
            pedal_time = sr_proc.get_pedal_time()
            #put the SR data in the row with the Syngo data
            row += [total_Dose, total_DAP, pedal_time]
            #tack the CPTs from the Syngo data on to the end
            row += [sr_proc.get_syngo().get_cpts_as_string()]
            table.append(row)
        return [table]
        

        
