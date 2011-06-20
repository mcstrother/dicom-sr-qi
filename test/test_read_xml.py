import unittest
import my_utils

class TestReadXML(unittest.TestCase):

    def setUp(self):
        self.procs = my_utils.get_procs('test')

    def test_attrs(self):
        self.assertEqual(self.procs[1].events[0].Number_of_Pulses,31)



if __name__ == '__main__':
    unittest.main()
