import unittest
from srqi.core import my_utils

class Test_my_utils(unittest.TestCase):

    def setUp(self):
        self.procs, _ = my_utils.get_procs('test')

    def test_average_fps(self):
        self.assertAlmostEqual(15.0, my_utils.average_fps(self.procs[1].get_fluoro_events()))

    def test_same_contents(self):
        a = [1,2,3]
        b = [1,2,3]
        self.assertTrue(my_utils.same_contents(a,b))
        self.assertFalse(my_utils.same_contents(a, b+[4]))
        self.assertTrue(my_utils.same_contents(a, b+[3]), "same_contents should ignore repeat values")

    def test_is_subset(self):
        self.assertTrue(my_utils.is_subset([1,2,3],[1,2,3,4]))
        self.assertTrue(my_utils.is_subset([1,2,3],[1,2,3]), "exact matches should count as subsets")
