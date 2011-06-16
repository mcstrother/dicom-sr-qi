import xlrd
import os
from datetime import datetime

print os.getcwd()

WB_NAME = "VRK.xls"

wb = xlrd.open_workbook(WB_NAME)
s = wb.sheet_by_name("Events")

table = []

for r in xrange(s.nrows):
	row_values = [s.cell(r,c).value for c in xrange(s.ncols) ]
	table.append(row_values)
	
print table[0]
print table[1]
print datetime(*xlrd.xldate_as_tuple(table[1][2],wb.datemode))

		