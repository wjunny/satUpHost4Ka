import unittest

import sys 
sys.path.append("..") 
import my_utils

class test_db_to_str(unittest.TestCase):
    def test1(self):
        self.assertEqual(my_utils.db_to_str(0), '0')
        self.assertEqual(my_utils.db_to_str(1), '0')
        self.assertEqual(my_utils.db_to_str(-0.5), '-0.5')
        self.assertEqual(my_utils.db_to_str(-1.1), '-1')
        self.assertEqual(my_utils.db_to_str(-2.3), '-2.5')
        self.assertEqual(my_utils.db_to_str(-2.2), '-2')
        self.assertEqual(my_utils.db_to_str(-4.7), '-4.5')
        self.assertEqual(my_utils.db_to_str(-5.8), '-6')
        self.assertEqual(my_utils.db_to_str(-31), '-31')
        self.assertEqual(my_utils.db_to_str(-31.2), '-31')
        self.assertEqual(my_utils.db_to_str(-31.3), '-31.5')

if __name__ == '__main__':
    unittest.main()