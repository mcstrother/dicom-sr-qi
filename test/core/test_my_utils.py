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
        self.assertTrue(my_utils.same_contents([2,1,3],b), "same_contents should ignore ordering")
        self.assertFalse(my_utils.same_contents(a, b+[4]))
        self.assertTrue(my_utils.same_contents(a, b+[3]), "same_contents should ignore repeat values")
        self.assertTrue(my_utils.same_contents([1],[1]), "same contents fails on lists of size 1")

    def test_is_subset(self):
        self.assertTrue(my_utils.is_subset([1,2,3],[1,2,3,4]))
        self.assertTrue(my_utils.is_subset([1,2,3],[1,2,3]), "exact matches should count as subsets")
        self.assertTrue(my_utils.is_subset([1],[1]), "is_subset fails on groups of size 1")
        self.assertTrue(my_utils.is_subset([1],[3,7,1]))

    def test_matches(self):
        self.assertTrue(my_utils.matches([444,-99], [444]))
        self.assertTrue(my_utils.matches(['444','-99'],['444']))
        self.assertFalse(my_utils.matches(['444','-99'],[444]))
        self.assertFalse(my_utils.matches(['444','-99'],[444,555]))


