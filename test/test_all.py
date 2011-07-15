import unittest
import os
import sys

if __name__ == '__main__':
    srqi_containing_dir = os.path.dirname(os.path.dirname(os.getcwd()))
    sys.path.append(srqi_containing_dir)
    loader = unittest.TestLoader()
    suite =  loader.discover(os.getcwd(), top_level_dir=os.path.dirname(os.getcwd()))
    unittest.TextTestRunner(verbosity=2).run(suite)


