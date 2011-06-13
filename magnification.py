import my_utils
import ReadXML
import csv
import matplotlib

def build_table():
        procs = ReadXML.process_file(my_utils.BJH_XML_FILE, my_utils.BJH_SYNGO_FILES)
        procs = procs + ReadXML.process_file(my_utils.SLCH_XML_FILE, my_utils.SLCH_SYNGO_FILES)
        #procs = ReadXML.process_file(my_utils.SLCH_XML_FILE, my_utils.SLCH_SYNGO_FILES)

        dose_lookup = {}
        exposure_lookup = {}
        DAP_lookup = {}
        for proc in procs:
                for e in proc.events:
                        if e.is_valid() and e.Irradiation_Event_Type == "Fluoroscopy":
                                if not e.iiDiameter in dose_lookup:
                                        dose_lookup[e.iiDiameter] = []
                                        exposure_lookup[e.iiDiameter] = []
                                        DAP_lookup[e.iiDiameter] = []
                                dose_lookup[e.iiDiameter].append(e.Dose_RP/e.Number_of_Pulses)
                                exposure_lookup[e.iiDiameter].append(e.Exposure/e.Number_of_Pulses)
                                DAP_lookup[e.iiDiameter].append(e.Dose_Area_Product/e.Number_of_Pulses)
        return (dose_lookup, exposure_lookup, DAP_lookup)

def write_csv(lookup):
        table = []
        for diameter, exposures in lookup.iteritems():
                row = [str(diameter)]
                row = row + [e for e in exposures]
                table.append(row)
        table = my_utils.transposed(table)
                
        with open("temp.csv",'wb') as f:
                w = csv.writer(f)
                w.writerows(table)

import matplotlib.pyplot as plt
def plot(lookup):
        data = []
        for iiDiameter in sorted(lookup.keys()):
                data.append(lookup[iiDiameter])
        plt.boxplot(data, sym='')
        plt.setp(plt.gca(),'xticklabels',sorted(lookup.keys()))
        plt.show()

def setup_DAP_axes():
        plt.title("DAP vs. Magnification")
        plt.xlabel("iiDiameter")
        plt.ylabel("DAP (Gy*m^2)")

def setup_exposure_axes():
        plt.title("Exposure vs. Magnification")
        plt.xlabel("iiDiameter")
        plt.ylabel("Exposure (uAs)")

def main():
        dose_lookup,exposure_lookup,DAP_lookup = build_table()
        plt.figure(1)
        #setup_DAP_axes()
        #plot(DAP_lookup)
        setup_exposure_axes()
        plot(exposure_lookup)
        #write_csv(DAP_lookup)

if __name__ == "__main__":
        main()
