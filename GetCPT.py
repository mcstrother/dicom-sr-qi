"""Given excel output from CARE and a bunch of excel files from syngo with CPT data
in them (formatted similarly to the files in the GetCPT Data folder--not the ones ending in 812),
use the patient ID number and the date of the procedure to assign CPT codes to each procedure
in the CARE file.

This is only useful to set up analysis for non-programmers.
Programmers should use ReadXML instead.
"""

import xlrd
import my_utils
import datetime

CPT_FILE_NAMES = ['./GetCPT Data/April_Output_Org.xls', './GetCPT Data/May_Output_Org.xls']
CARE_FILE_NAME = "all bjh with CPT and time.xls"

def get_CPTs_from_file(file_name):
	"""Returns a dict mapping (PatientId(int),start_date(datetime.date)) --> cpts(string)
	"""
	#Get the sheet
	wb = xlrd.open_workbook(file_name)
	s = wb.sheet_by_index(1)
	#Get headings and column numbers
	headings = [c.value for c in s.row(0)]
	mpi_column = headings.index("MPI")
	start_date_column = headings.index("DOS Start")
	cpts_column = headings.index("CPTs")
	#Build dictionary
	out = {}
	for r in xrange(1,s.nrows):
		mpi = int(s.cell(r,mpi_column).value)
		sd = s.cell(r,start_date_column).value
		date_tuple = xlrd.xldate_as_tuple(sd,wb.datemode)[:3]
		sd = datetime.date(*date_tuple)#convert from xl to python date
		cpts = s.cell(r,cpts_column).value
		out[(mpi, sd)] = cpts
	return out

def get_CPTs_from_files(file_names):
	lookup = {}
	for file_name in file_names:
		lookup.update(get_CPTs_from_file(file_name))
	return lookup
	
def add_CPTs_to_care(care_file_name, lookup):
	wb = xlrd.open_workbook(care_file_name)
	s = wb.sheet_by_index(0)
	out = []
	out.append("CPTs")
	for r in xrange(1,s.nrows):
		good_pid = False
		try:
			pid = int(s.cell(r,0).value)
			good_pid = True
		except ValueError:
			pass
		date = s.cell(r,2).value
		date = my_utils.care_date_to_python_date(date)
		if good_pid and (pid, date) in lookup:
			out.append("'"+lookup[(pid,date)])
		else:
			out.append('Not found')
	return out

def main():
	lookup = get_CPTs_from_files(CPT_FILE_NAMES)
	cpts = add_CPTs_to_care(CARE_FILE_NAME, lookup)
	for cpt in cpts:
		print cpt
	
if __name__ == "__main__":
	main()