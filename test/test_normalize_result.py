import unittest
import yaml
import numpy as np
import math

import sys 
sys.path.append("..") 
import calibration

class test_normalize_result(unittest.TestCase):
    def test(self):
        test_data = {}
        test_data['G11_A1H'] = {'phase':0.2, 'gain': 0.5}
        test_data['G11_A2H'] = {'phase':0, 'gain': 0.45}
        test_data['G11_A3H'] = {'phase':3.2, 'gain': 0.49}
        test_data['G11_A4H'] = {'phase':5.2, 'gain': 0.44}

        dec = [10*math.log10(0.44/0.5), 10*math.log10(0.44/0.45), 10*math.log10(0.44/0.49), 10*math.log10(0.44/0.44)]
        error = [5.2-0.2, 5.2-0, 5.2-3.2, 5.2-5.2]
      
        calibration.normalize_result(test_data)

        self.assertAlmostEqual(test_data['G11_A1H']['phase'], error[0])
        self.assertAlmostEqual(test_data['G11_A2H']['phase'], error[1])
        self.assertAlmostEqual(test_data['G11_A3H']['phase'], error[2])
        self.assertAlmostEqual(test_data['G11_A4H']['phase'], error[3])

        self.assertAlmostEqual(test_data['G11_A1H']['gain'], dec[0])
        self.assertAlmostEqual(test_data['G11_A2H']['gain'], dec[1])
        self.assertAlmostEqual(test_data['G11_A3H']['gain'], dec[2])
        self.assertAlmostEqual(test_data['G11_A4H']['gain'], dec[3])

        print(test_data)
           
if __name__ == '__main__':
    unittest.main()