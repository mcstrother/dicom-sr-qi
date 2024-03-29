from srqi.core import inquiry
from srqi.core.Parse_Syngo import Syngo
from srqi.core import my_utils
from os import path

class Combine_Sr_Syngo(inquiry.Inquiry):


    def run(self, sr_procs, context, extra_procs):
        self.sr_procs = sr_procs
        self.extra_syngo = [p for p in extra_procs if isinstance(p, Syngo)]

    def get_tables(self):
        #get the standard heading list except for the last entry, which is 'CPTs'
        first_syngo= None
        for p in self.sr_procs:
            if p.has_syngo():
                first_syngo = p.get_syngo()
                break
        if first_syngo is None:
            if len(self.extra_syngo) >0:
                first_syngo = self.extra_syngo[0]
            else:
                raise Exception("No syngo data found")
        headings = first_syngo.get_heading_list()[:-1]
        headings += ["SeriesInstanceUID","Total Dose (Gy)(SR)", "Total DAP (Gym2)(SR)", "Pedal Time (s)(SR)",
                     "Fluoro Dose (Gy)(SR)", "Fluoro DAP (Gym2)(SR)", "Fluoro Exposure Time (ms)"]
        headings += ["CPTs"]
        table = [headings]
        for sr_proc in self.sr_procs:
            if not sr_proc.has_syngo():
                continue
            # init row with all data from Syngo except CPTs
            row = []
            syngo = sr_proc.get_syngo()
            row += syngo.get_data_list()[:-1]
            #get the data we need from SR
            total_Dose = sr_proc.get_total_Dose()
            total_DAP = sr_proc.get_total_DAP()
            pedal_time = sr_proc.get_pedal_time()
            total_fluoro_DAP = sum([e.Dose_Area_Product for e in sr_proc.get_fluoro_events()])
            total_fluoro_dose = sum([e.Dose_RP for e in sr_proc.get_fluoro_events()])
            total_fluoro_time = sum([e.Exposure_Time for e in sr_proc.get_fluoro_events()])
            series_instance_UID = sr_proc.SeriesInstanceUID
            #put the SR data in the row with the Syngo data
            row += [series_instance_UID, total_Dose, total_DAP, pedal_time,
                    total_fluoro_dose, total_fluoro_DAP, total_fluoro_time]
            #tack the CPTs from the Syngo data on to the end
            row += [syngo.get_cpts_as_string()]
            table.append(row)
        for syngo in self.extra_syngo:
            row = []
            row += syngo.get_data_list()[:-1]
            row += ['']*7
            row += [syngo.get_cpts_as_string()]
            table.append(row)
        my_utils.write_csv(table, path.join(my_utils.get_output_directory(), "output.csv"))
        return [table]
        

        
