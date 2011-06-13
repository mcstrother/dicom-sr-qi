import datetime
import xlrd

class Syngo_Procedure_Data(object):
	IVRFU_CPT = "-99999"
	
	def __init__(self, MPI, RAD1, RAD2, DOS_Start, CPTs, DOS_Time):
                if not isinstance(MPI,int):
                        raise TypeError("Invalid type for MPI. Expected int, received " + str(type(MPI)))
		self.MPI = MPI #should always be an int
		self.RAD1 = RAD1
		self.RAD2 = RAD2
		self.DOS_Start = DOS_Start#datetime.date
		self.DOS_Time = DOS_Time #datetime.time
		if CPTs.__class__ == ''.__class__:
			self.CPTs = self._CPTs_from_string(CPTs)
		else:
			self.CPTs = CPTs
	
	def _CPTs_from_string(self, cpts_string):
		cpts = cpts_string.split(',')
		out = []
		for cpt in cpts:
			if cpt == "IVRFU":
				out.append(self.IVRFU_CPT)
			else:
				out.append(int(cpt))
		return cpts

        def get_start(self):
                """Returns a Python datetime
                object representing the start
                of the procedure
                """
                return datetime.datetime.combine(self.DOS_Start, self.DOS_time)

_COLUMNS = ["MPI","RAD1","RAD2","DOS Start","CPTs", "DOS Time"]
		
def parse_syngo_file(file_name):
	wb = xlrd.open_workbook(file_name)
	s = wb.sheet_by_index(1)
	headings = [c.value for c in s.row(0)]
	column_numbers = {}
	for col_name in _COLUMNS:
		column_numbers[col_name] = headings.index(col_name)
	procedures = []
	for r in xrange(1,s.nrows):
		mpi = int(s.cell(r,column_numbers["MPI"]).value)
		sd = s.cell(r,column_numbers["DOS Start"]).value
		date_tuple = xlrd.xldate_as_tuple(sd,wb.datemode)[:3]
		sd = datetime.date(*date_tuple)#convert from xl to python date
		cpts = s.cell(r,column_numbers["CPTs"]).value
		rad1 = s.cell(r,column_numbers["RAD1"]).value
		rad2 = s.cell(r,column_numbers["RAD2"]).value
                dos_time_tuple = xlrd.xldate_as_tuple(s.cell(r,column_numbers["DOS Time"]).value, wb.datemode)
                dos_time = datetime.time(hour = dos_time_tuple[-3],minute=dos_time_tuple[-2],second=dos_time_tuple[-1])
		procedures.append(Syngo_Procedure_Data(mpi,rad1,rad2,sd,cpts,dos_time))
	return procedures
	
	


def parse_syngo_files(file_names):
	out = []
	for name in file_names:
		out = out + parse_syngo_file(name)
	return out
