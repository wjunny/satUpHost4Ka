import unittest
import timeit
import sys 
sys.path.append("..") 
import my_utils

class test_channel_name(unittest.TestCase):
    def test1(self):
        self.assertEqual(my_utils.group_channel_name(2, 1, 'H'), ('G21_A1H', 'G21_A2H', 'G21_A3H', 'G21_A4H'))

    def test2(self):
        self.assertEqual(my_utils.all_channel_name('V')[:4], ('G11_A1V', 'G11_A2V', 'G11_A3V', 'G11_A4V')) 
        self.assertEqual(my_utils.all_channel_name('H')[252:256], ('G88_A1H', 'G88_A2H', 'G88_A3H', 'G88_A4H'))

    def test3(self):
        self.assertEqual(my_utils.block_channel_name(my_utils.BLOCK1, 'V')[0:16], 
            ('G14_A1V', 'G14_A2V', 'G14_A3V', 'G14_A4V', 
             'G13_A1V', 'G13_A2V', 'G13_A3V', 'G13_A4V', 
             'G24_A1V', 'G24_A2V', 'G24_A3V', 'G24_A4V', 
             'G23_A1V', 'G23_A2V', 'G23_A3V', 'G23_A4V'))
        self.assertEqual(my_utils.block_channel_name(my_utils.BLOCK2, 'H')[0:16], 
            ('G18_A1H', 'G18_A2H', 'G18_A3H', 'G18_A4H', 
             'G17_A1H', 'G17_A2H', 'G17_A3H', 'G17_A4H', 
             'G28_A1H', 'G28_A2H', 'G28_A3H', 'G28_A4H', 
             'G27_A1H', 'G27_A2H', 'G27_A3H', 'G27_A4H'))
        self.assertEqual(my_utils.block_channel_name(my_utils.BLOCK3, 'V')[0:16], 
            ('G54_A1V', 'G54_A2V', 'G54_A3V', 'G54_A4V', 
             'G53_A1V', 'G53_A2V', 'G53_A3V', 'G53_A4V', 
             'G64_A1V', 'G64_A2V', 'G64_A3V', 'G64_A4V', 
             'G63_A1V', 'G63_A2V', 'G63_A3V', 'G63_A4V'))
        self.assertEqual(my_utils.block_channel_name(my_utils.BLOCK4, 'V')[0:16], 
            ('G58_A1V', 'G58_A2V', 'G58_A3V', 'G58_A4V', 
             'G57_A1V', 'G57_A2V', 'G57_A3V', 'G57_A4V', 
             'G68_A1V', 'G68_A2V', 'G68_A3V', 'G68_A4V', 
             'G67_A1V', 'G67_A2V', 'G67_A3V', 'G67_A4V'))
     
if __name__ == '__main__':
    unittest.main()