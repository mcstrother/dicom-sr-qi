import unittest
from mirqi.core import my_utils, Parse_Syngo
from mirqi.inquiries import operator_improvement
from mirqi import test
import os
from datetime import date

class Test_Operator_Improvement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_dir = os.path.join(os.path.dirname(test.__file__),'data')
        data_file = os.path.join(data_dir, 'test_operator_improvement.xls')
        syngo_procs = Parse_Syngo.parse_syngo_file(data_file)
        inq_cls = operator_improvement.Operator_Improvement
        inq_cls.PROCS_PER_WINDOW.value = 3
        inq_cls.MIN_REPS.value = 4
        cls.inq = operator_improvement.Operator_Improvement([],
                                                             extra_procs = syngo_procs)

    def test_num_rads(self):
        self.assertEquals(len(self.inq.lookup),2)

    def test_stewart(self):
        expected = [(date(2011,5,15),4.5),
                    (date(2011,5,22),4),
                    (date(2011,5,24),.5),
                    (date(2011,5,28),-2),
                    (date(2011,5,29),-1)]
        equal = self._lists_equal(self.inq.lookup['Stewart, J.'], expected)
        self.assertTrue(equal, "Incorect metrics for Stewart. Expected :\n " + str(expected) + "\n Got \n" + str(self.inq.lookup['Stewart, J.']))

    def test_rayner(self):
        expected = [(date(2011,6,5), 1.5),
                    (date(2011,6,8), 1.5)]
        equal = self._lists_equal(self.inq.lookup['Rayner, K.'], expected)
        self.assertTrue(equal, "Incorect metrics for Rayner. Expected :\n " + str(expected) + "\n Got \n" + str(self.inq.lookup['Rayner, K.']))


    def _lists_equal(self, out, expected):
        failed = False
        for out, expected in zip(out,expected):
            if not out[0] == expected[0]:
                failed = True
                break
            elif not abs(expected[1]-out[1]) <.000001:
                failed = True
                break
        return not failed
    

if __name__ == '__main__':
    unittest.main()

