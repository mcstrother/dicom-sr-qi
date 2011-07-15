import unittest
from srqi.core import my_utils, Parse_Syngo
from srqi.inquiries import operator_improvement
from srqi import test
import os
from datetime import date

class Test_Operator_Improvement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_dir = os.path.join(os.path.dirname(test.__file__),'data')
        data_file = os.path.join(data_dir, 'test_operator_improvement.xls')
        syngo_procs = Parse_Syngo.parse_syngo_file(data_file)
        cls.syngo_procs = syngo_procs
        inq_cls = operator_improvement.Operator_Improvement
        inq_cls.PROCS_PER_WINDOW.value = 3
        inq_cls.MIN_REPS.value = 4
        cls.inq_cls = inq_cls
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

    def test_get_procedures_helper(self):
        cpt_to_procs = operator_improvement.get_procedures_helper([], self.syngo_procs,
                                                         self.inq_cls.MIN_REPS.value)
        expected_cpt_list = ['1','2']
        self.assertEqual(set(expected_cpt_list),set(cpt_to_procs.keys()),
                        """get_procedures_helper returned an incorrect list of included cpt codes.
                        Expected: """ + str(expected_cpt_list) +"\n Got: " + str(cpt_to_procs.keys()))
        self.assertEqual(13, sum(map(len,cpt_to_procs.values())),
                         "Total number of procedures returned by get_procedures helper is incorrect.")
        
    def test_sort_by_rads_helper(self):
        cpt_to_procs = operator_improvement.get_procedures_helper([],
                                                                  self.syngo_procs,
                                                                  self.inq_cls.MIN_REPS.value)
        syngo_procs = sum(cpt_to_procs.values(),[])
        rad1_to_procs = operator_improvement.sort_by_rads_helper(syngo_procs,
                                                                 self.inq_cls.PROCS_PER_WINDOW.value)
        self.assertEqual(len(sum(rad1_to_procs.values(),[])),12,
                         "Incorrect total number of procedures found by sort_by_rads_helper")
                

    def test_get_procedure_windows(self):
        STEP_SIZE = 2
        cpt_to_procs = operator_improvement.get_procedures_helper([],
                                                                  self.syngo_procs,
                                                                  self.inq_cls.MIN_REPS.value)
        syngo_procs = sum(cpt_to_procs.values(),[])
        rad1_to_procs = operator_improvement.sort_by_rads_helper(syngo_procs,
                                                                 self.inq_cls.PROCS_PER_WINDOW.value)
        for i,proc_list in enumerate(rad1_to_procs.values()):
            if not i==len(proc_list)-1:
                windows = operator_improvement.get_procedure_windows(proc_list,
                                                                     self.inq_cls.PROCS_PER_WINDOW.value,
                                                                     STEP_SIZE)
                for window in windows:
                    self.assertEqual(len(window), self.inq_cls.PROCS_PER_WINDOW.value,
                                     "get_procedure_windows returns windows of incorrect length")
        stew_windows = operator_improvement.get_procedure_windows(rad1_to_procs['Stewart, J.'],
                                                                     self.inq_cls.PROCS_PER_WINDOW.value,
                                                                     STEP_SIZE)
        self.assertEqual(sorted([4,5,1]), [p.fluoro for p in stew_windows[0]])
        self.assertEqual(sorted([1,1,4]), [p.fluoro for p in stew_windows[1]])
        self.assertEqual(sorted([4,1,2]), [p.fluoro for p in stew_windows[2]])
        self.assertEqual(len(stew_windows),3)
        
        

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

