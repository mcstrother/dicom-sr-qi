"""Given a .xls file exported from CARE, calculate the
procedure duration for all of the procedures listed in
the "Patients" sheet. The output is printed so it can be
directly copied into a new column in the workbook.

This is only useful to set up analysis for non-programmers.
Programmers should use ReadXML instead.

"""
import xlrd
import my_utils

FILE_NAME = 'all bjh with cpt and time.xls'


def build_time_lookup(wb):
	"""Given a properly formatted workbook with events,
	build and return a dictionary where keys are 
	StudyInstanceUIDs and values are the lenggths of the studies.
	"""
	s = wb.sheet_by_index(1)
	current_id = s.cell(1,2).value
	start_time = my_utils.care_datetime_to_python_datetime(s.cell(1,5).value)
	end_time = start_time
	time_dict = {}
	for r in xrange(2,s.nrows):
		this_id = s.cell(r,2).value
		if this_id == current_id:
			end_time = my_utils.care_datetime_to_python_datetime(s.cell(r,5).value)
		else:
			time_dict[current_id] = end_time-start_time
			current_id = s.cell(r,2).value
			start_time = my_utils.care_datetime_to_python_datetime(s.cell(r,5).value)
			end_time = start_time
	time_dict[current_id] = end_time-start_time #add the last one
	return time_dict

	
def print_output(wb, lookup):
	s = wb.sheet_by_index(0)
	print 'Duration'
	for r in xrange(1,s.nrows):
		try:
			print lookup[s.cell(r,9).value]
		except KeyError:
			print ''
	
if __name__ == '__main__':
	wb = xlrd.open_workbook(FILE_NAME)
	lookup = build_time_lookup(wb)
	print_output(wb, lookup)



		