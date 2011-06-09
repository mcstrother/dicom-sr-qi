import my_utils
import ReadXML
import csv

procs = ReadXML.process_file(my_utils.BJH_XML_FILE, my_utils.BJH_SYNGO_FILES)
procs = procs + ReadXML.process_file(my_utils.SLCH_XML_FILE, my_utils.SLCH_SYNGO_FILES)
#procs = ReadXML.process_file(my_utils.SLCH_XML_FILE, my_utils.SLCH_SYNGO_FILES)


out = [("iiDiameter","Exposure per frame")]
lookup = {}
for proc in procs:
	for e in proc.events:
		if e.is_valid() and e.Irradiation_Event_Type == "Fluoroscopy":
			out.append((e.iiDiameter, e.Dose_RP/e.Number_of_Pulses))
			if not e.iiDiameter in lookup:
				lookup[e.iiDiameter] = []
			lookup[e.iiDiameter].append(e.Dose_RP/e.Number_of_Pulses)
table = []
for diameter, exposures in lookup.iteritems():
	row = [str(diameter)]
	row = row + [e for e in exposures]
	table.append(row)
table = my_utils.transposed(table)
	
with open("temp.csv",'wb') as f:
	w = csv.writer(f)
	w.writerows(table)