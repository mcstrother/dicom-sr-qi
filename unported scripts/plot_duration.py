"""Write a .csv file that allows us to easily make a box plot
of the duration of the most common CPT code combinations.
"""
import srdata
import csv

XML_FILE_NAME = 'all bjh.xml'
CPT_FILE_NAMES = CPT_FILE_NAMES = ['./GetCPT Data/April_Output_Org.xls', './GetCPT Data/May_Output_Org.xls']


def main():
	procs = srdata.process_file(XML_FILE_NAME, CPT_FILE_NAMES)
	#sort the procedures by their CPT code combinations
	procs_by_cpt = {}
	for proc in procs:
		if not proc.get_cpts() in procs_by_cpt:
			procs_by_cpt[proc.get_cpts()] = []
		procs_by_cpt[proc.get_cpts()].append(proc)
	#write a table of CPT code combinations followed by all the durations of the associated procedures
	table = []
	for (cpts, proc_list) in procs_by_cpt.iteritems():
		row_header = "'" +','.join([str(x) for x in cpts])
		row = [row_header] + [proc.get_duration() for proc in proc_list if not proc.get_duration() is None]
		if len(row)>4:
			table.append(row)
	writer = csv.writer(open('output.csv','wb'))
	writer.writerows(table)

if __name__ == '__main__':
	main()