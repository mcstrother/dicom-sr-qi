import unittest
from mirqi.gui import report_writer
from mirqi.inquiries import missing_data_inquiry, average_fps
from mirqi.core import my_utils

class Test_Report_Writer(unittest.TestCase):
    
    def setUp(self):
        self.procs, _ = my_utils.get_procs('test')
        self.inq1 = missing_data_inquiry.Missing_Data_Inquiry(self.procs)
        self.inq2 = average_fps.Average_Fps(self.procs)
    
    def test_write_single(self):
        report_writer.write_report([self.inq1])
    
    
    def test_write_two_singles(self):
        report_writer.write_report([self.inq1])
        report_writer.write_report([self.inq2])
    
    
    def test_write_two_of_same_singles(self):
        report_writer.write_report([self.inq2])
        report_writer.write_report([self.inq2])
    
    
    def test_write_multiple_of_same(self):
        report_writer.write_report([self.inq1, self.inq1])

    def test_write_multiple_of_same2(self):
        report_writer.write_report([self.inq2, self.inq2])
    
    def test_write_multiple(self):
        # just testing for exceptions here        
        report_writer.write_report([self.inq2, self.inq1])


