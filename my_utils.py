from datetime import datetime, date, timedelta
import csv

BJH_SYNGO_FILES = ['./Data/BJH/April_Output_Org.xls', './Data/BJH/May_Output_Org.xls']
BJH_XML_FILE = './Data/BJH/all bjh.xml'
SLCH_SYNGO_FILES = ['./Data/SLCH/April_IR_Output_Org.xls', './Data/SLCH/May_IR_Output_Org.xls']
SLCH_XML_FILE = './Data/SLCH/all slch.xml'

def care_datetime_to_python_datetime(care_date):
	care_date = str(care_date)
	return datetime(int(care_date[:4]),int(care_date[4:6]),int(care_date[6:8]),int(care_date[8:10]),int(care_date[10:12]), int(care_date[12:14]))
	
def care_date_to_python_date(care_date):
	care_date = str(care_date)
	return date(int(care_date[:4]),int(care_date[4:6]),int(care_date[6:8]))
	
def write_csv(table, file_name = 'output.csv'):
	writer = csv.writer(open(file_name,'wb'))
	writer.writerows(table)
	
def total_seconds(time_delta):
	td = time_delta
	return (td.microseconds + (td.seconds + td.days * 24 * 3600.0) * 10**6) / 10**6
	
def multiply_timedelta(td, x):
	return timedelta(days = td.days *x, seconds = td.seconds*x, microseconds = td.microseconds *int(x))
	
def transposed(lists):
   if not lists: return []
   return map(lambda *row: list(row), *lists)