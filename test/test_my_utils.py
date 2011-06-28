import unittest
from mirqi.core import my_utils

class TestReadXML(unittest.TestCase):

    def setUp(self):
        self.procs = my_utils.get_procs('test')

    def test_average_fps(self):
        self.assertAlmostEqual(15.0, my_utils.average_fps(self.procs[1].get_fluoro_events()))
        #print my_utils.average_fps(self.procs[1].get_events())


if __name__ == '__main__':
    unittest.main()
