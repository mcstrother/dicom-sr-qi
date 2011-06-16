import datetime
import xlrd

class Syngo(object):
        IVRFU_CPT = "-99999"
        _INT_ATTRS = ["MPI", "MRN", "ACC","FLUORO"]
        _IGNORED_ATTRS = ["KAR","KAP","Ima","DLP","CTDI","Procedure"]
        _STRING_ATTRS =["RAD1","RAD2","TECH","LOCATION","DEPT"]
        _DATETIME_PAIR_ATTRS = [("DOS Start", "DOS Time"),("End DATE", "End Time"),("READ DATE", "Read Time"),("SIGN DATE","Sign Time"),("ADD DATE","Add Time")]
        _OTHER_ATTRS = ["CPTs"]
        _ALL_ATTRS = _INT_ATTRS + _STRING_ATTRS + _OTHER_ATTRS #note absence of + _IGNORED_ATTRS
        for pair in _DATETIME_PAIR_ATTRS:
                _ALL_ATTRS.append(pair[0])
                _ALL_ATTRS.append(pair[1])
        
        
        def __init__(self, *args):
                if isinstance(args[0],dict) and len(args) ==1:
                        self._init_from_dict(args[0])
                elif isinstance(args[0],list) and isinstance(args[1],dict) and len(args) ==3:#list of xlrd.sheet.Cell objects with a dict identifying the column numbers
                        self._init_from_row(args[0], args[1], args[2])
                else:
                        raise ValueError("Invalid inputs to Syngo.__init__")
                """if not isinstance(MPI,int):
                        raise TypeError("Invalid type for MPI. Expected int, received " + str(type(MPI)))
                self.MPI = MPI #should always be an int
                self.RAD1 = RAD1
                self.RAD2 = RAD2
                self.DOS_Start = DOS_Start#datetime.date
                self.DOS_Time = DOS_Time #datetime.time
                self.end_date = end_date #datetime.date
                self.end_time = end_time #datetime.time
                if isinstance(CPTs, basestring):
                        self.CPTs = self._CPTs_from_string(CPTs)
                else:
                        self.CPTs = CPTs"""
        
        def _CPTs_from_string(self, cpts_string):
                cpts = cpts_string.split(',')
                out = []
                for cpt in cpts:
                        if cpt == "IVRFU":
                                out.append(self.IVRFU_CPT)
                        else:
                                out.append(int(cpt))
                return out

        def get_start(self):
                """Returns a Python datetime
                object representing the start
                of the procedure
                """
                return datetime.datetime.combine(self.DOS_Start, self.DOS_Time)
        def get_end(self):
                """Returns a Python datetime
                object representing the end
                of the procedure
                """
                return datetime.datetime.combine(self.end_date, self.end_time)

        def _init_from_dict(self,d):
                """
                d - dict(attribute name -> attribute value)
                The int and cpt values in d do not have to be of the correct type,
                but they must be able to be re-interpreted as the correct
                type.
                d must have a key for every string in self._ALL_ATTRS
                """
                for attr in self._STRING_ATTRS:
                        setattr(self,attr.replace(' ','_').lower(),d[attr])
                for attr in self._INT_ATTRS:
                        if d[attr] == "IVRFU":
                                value = self.IVRFU_CPT
                        elif d[attr] is None:
                                value = None
                        else:
                                value = int(d[attr])
                        setattr(self,attr.replace(' ','_').lower(),value)
                for date_attr, time_attr in self._DATETIME_PAIR_ATTRS:
                        setattr(self,date_attr.replace(' ','_').lower(),d[date_attr])
                        setattr(self,time_attr.replace(' ','_').lower(),d[time_attr])
                        combined_attr = time_attr.split(' ')[0].lower()
                        if d[date_attr] and d[time_attr]:
                                try:
                                        combined_value = datetime.datetime.combine(getattr(self,date_attr.replace(' ','_').lower()),getattr(self,time_attr.replace(' ','_').lower()))
                                except TypeError as te:
                                        print time_attr
                                        print d[time_attr]
                                        raise te
                                setattr(self,combined_attr,combined_value)
                        else:
                                setattr(self,combined_attr,None)
                cpts = d["CPTs"]
                if isinstance(cpts, basestring):
                        self.cpts = self._CPTs_from_string(cpts)
                else:
                        self.cpts = cpts

        def _init_from_row(self,r,col_nums,datemode):
                """Initialize from a list of xlrd.Sheet.Cell objects
                """
                d = {}
                for attr in self._ALL_ATTRS:
                        value = r[col_nums[attr]].value
                        if not value == '':
                                d[attr] = value
                        else:
                                d[attr] = None
                for date_attr,time_attr in self._DATETIME_PAIR_ATTRS:
                        if not d[date_attr] is None and not isinstance(d[date_attr], basestring):#TODO: could probably handle these strings better to actually extrac their data
                                date_tuple = xlrd.xldate_as_tuple(d[date_attr],datemode)
                                date = datetime.date(year = date_tuple[0],month=date_tuple[1],day=date_tuple[2])
                                d[date_attr] = date
                        else:
                                d[date_attr] = None
                        if not d[time_attr] is None and not isinstance(d[time_attr],basestring):
                                time_tuple = xlrd.xldate_as_tuple(d[time_attr],datemode)
                                time = datetime.time(hour=time_tuple[-3],minute=time_tuple[-2],second=time_tuple[-1])
                                d[time_attr] = time
                        else:
                                d[time_attr] =None
                self._init_from_dict(d)
                
        def get_data_list(self):
                """Return a list of all of the data in the object
                so that it can be written to a row of an excel or csv
                object
                """
                attr_list = [x.lower().replace(' ','_') for x in self.get_heading_list()]
                out = []
                for attr in attr_list:
                        if attr == 'cpts':
                                out.append(','.join([str(x) for x in self.cpts]))
                        else:
                                out.append(getattr(self,attr))
                return out

        def get_heading_list(self):
                """Return a list of column headings as
                they appear in processed Syngo output
                """
                return  ['MPI', 'MRN', 'RAD1', 'RAD2', 'ACC', 'DOS Start', 'DOS Time', \
                         'End DATE', 'End Time', 'READ DATE', 'Read Time', 'SIGN DATE',\
                         'Sign Time', 'ADD DATE','Add Time', 'TECH', 'LOCATION', 'DEPT',\
                         'FLUORO', 'CPTs']
        
        
_COLUMNS = Syngo._ALL_ATTRS

                
def parse_syngo_file(file_name):
        wb = xlrd.open_workbook(file_name)
        s = wb.sheet_by_index(1)
        headings = [c.value for c in s.row(0)]
        column_numbers = {}
        for col_name in _COLUMNS:
                column_numbers[col_name] = headings.index(col_name)
        procedures = []
        for r in xrange(1,s.nrows):
                procedures.append(Syngo(s.row(r),column_numbers,wb.datemode))
        return procedures
        
        


def parse_syngo_files(file_names):
        out = []
        for name in file_names:
                out = out + parse_syngo_file(name)
        return out

import xlwt
def write_syngo_file(file_name, sdict):
        """Write an excel file of Syngo data similar
        to the syngo files that we normally read in.

        file_name - the name of file to be written (usually ending in .xls)
        sdict - sheet_name(string)->syngo_list(list of syngo objects)
        """
        wb = xlwt.Workbook()
        for sheet_name, slist in sdict.iteritems():
                sheet = wb.add_sheet(sheet_name)
                for i,heading in enumerate(slist[0].get_heading_list()):
                        sheet.write(0,i,heading)
                for r,syngo in enumerate(slist):
                        for c,data in enumerate(syngo.get_data_list()):
                                xf=None
                                if isinstance(data, datetime.date):
                                        xf = xlwt.easyxf(num_format_str='MM/DD/YYYY')
                                elif isinstance(data, datetime.time):
                                        xf = xlwt.easyxf(num_format_str='HH:MM:SS')
                                elif isinstance(data, datetime.datetime):
                                        xf = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')
                                if xf:
                                        sheet.write(r+1,c,data, xf)
                                else:
                                        sheet.write(r+1,c,data)
        wb.save(file_name)

        