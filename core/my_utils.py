from datetime import datetime, date, timedelta
import csv
import mirqi
import ReadXML
import os


def get_output_directory():
        return os.path.join(os.path.abspath(mirqi.__path__[0]), 'output')

def get_data_directory():
        return os.path.join(os.path.abspath(mirqi.__path__[0]),'Data')

_dir = os.path.abspath(mirqi.__path__[0])

BJH_SYNGO_FILES = [os.path.join(_dir,'Data/BJH/April_Output_Org.xls'), os.path.join(_dir,'Data/BJH/May_Output_Org.xls')]
BJH_XML_FILE = os.path.join(_dir,'Data/BJH/all bjh.xml')
SLCH_SYNGO_FILES = [os.path.join(_dir,'Data/SLCH/April_IR_Output_Org.xls'), os.path.join(_dir,'Data/SLCH/May_IR_Output_Org.xls')]
SLCH_XML_FILE = os.path.join(_dir,'Data/SLCH/all slch.xml')
TEST_XML_FILE = os.path.join(_dir,'Data/sample.xml')
TEST_SYNGO_FILES = [os.path.join(_dir,'Data/sample_syngo.xls')]

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

def get_procs(group = 'all'):
        if group == 'bjh':
                procs = ReadXML.process_file(BJH_XML_FILE, BJH_SYNGO_FILES)
        elif group == 'slch':
                procs = ReadXML.process_file(SLCH_XML_FILE, SLCH_SYNGO_FILES)
        elif group == 'all':
                procs = ReadXML.process_file(BJH_XML_FILE, BJH_SYNGO_FILES)
                procs = procs + ReadXML.process_file(SLCH_XML_FILE, SLCH_SYNGO_FILES)
        elif group == 'test':
                procs = ReadXML.process_file(TEST_XML_FILE, TEST_SYNGO_FILES)
        else:
                raise ValueError("Invalid group")
        return procs


def average_fps(events):
        """Gets the average FPS weighted by event duration"""
        if len(events) == 0:
                raise ValueError("Cannot take average of empyt list")
        total_fluoro_time = sum([e.get_duration() for e in events],timedelta(0) )
        total_fluoro_seconds = total_seconds(total_fluoro_time)
        mean_numerator = sum([multiply_timedelta(e.get_duration(),e.Pulse_Rate) for e in events], timedelta(0))
        return total_seconds(mean_numerator)/total_fluoro_seconds


def is_subset(list1, list2):
    """Returns true if list 1 is a subset of list 2
    (assumes neither list has any repeats)
    """
    for item in list1:
        if not item in list2:
            return False
    return True

def same_contents(list1,list2):
    """Returns true if list 1 has the exact same
    contents as list 2. (assumes neither list has
    any repeats)
    """
    if not len(list1) == len(list2):
        return False
    return is_subset(list1,list2)

def matches(list1,list2):
    """Returns is_subset or same_contents
    depending on whether or not the last
    item in list1 is -99
    """
    if list1[-1] == -99:
        return same_contents(list1[:-1],list2)
    else:
        return is_subset(list1,list2)

import numbers
def standard_cpt(cpt):
        """Given a cpt code as an integer, float
        or string, convert it to a string in a
        standard format.
        * no leading or trailing whitespace
        * no '.0' at the end of integers
        * letters are all capitalized
        """
        if isinstance(cpt, numbers.Number):
                return str(int(cpt))
        elif isinstance(cpt,basestring):
                out = cpt.split('.')[0]
                out = out.strip()
                out = out.upper()
                return out

def organize(iterable, key):
        """Put all of the elements in `iterable` into
        a dictionary which maps possible return values
        of key onto lists of items of iterable

        iterable - any iterable object (e.g. a list, or tuple)
        key - a function that takes items in interable as inputs

        Example:
        organize([1,2,3],lambda x: x==2)
        {True:[1,3],False:[2]}
        """
        out = {}
        for item in iterable:
                k = key(item)
                if not k in out:
                        out[k] = []
                out[k].append(item)
        return out

import xlrd

def coerce_human_date(d, datemode = None):
        """Attempt to coerce d into a Python datetime.date
        
        Generally d will have been retrieved from an excel
        spreadsheet, so I expect it to be a string or an
        excel date.

        Args:
                d - object to be coerced
                datemode - optional xlrd datemode object
        """
        if d is None:
                raise ValueError("Cannot coerce None into date.")
        if isinstance(d, date):
                return d
        if isinstance(d, basestring):
                raise NotImplementedError("Can't coerce string into a date... yet")
        date_tuple = xlrd.xldate_as_tuple(d,datemode)
        return date(year = date_tuple[0],
                             month=date_tuple[1],
                             day=date_tuple[2])

_ARB_DATE = date(2000,1,1) # an arbitrary date
def subtract_times(t1, t2):
        """returns a datetime.timedelta object representing t1-t2
        """
        t1 = datetime.combine(_ARB_DATE, t1)
        t2 = datetime.combine(_ARB_DATE, t2)
        return t1-t2

import pkgutil
import mirqi.inquiries
def get_inquiry_classes():
        """Get a list of inquiry classes
        """
        pkgpath = os.path.dirname(mirqi.inquiries.__file__)
        inq_module_names = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]
        temp = __import__('mirqi.inquiries', globals(), locals(), inq_module_names,-1)
        inq_modules = [getattr(temp, name) for name in inq_module_names]
        inq_classes = [getattr(module,dir(module)[0]) for module in inq_modules]
        assert inq_module_names == [inq_class.__name__.lower() for inq_class in inq_classes]
        return inq_classes
