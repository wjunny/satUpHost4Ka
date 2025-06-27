import unittest
import numpy as np
import bitstring

import sys 
sys.path.append("..") 
import paa_control
import channel_mapping
import my_utils

class test_write_array_phase(unittest.TestCase):
   paa = paa_control.PAAControl('COM13', 'Receiving', 8) 

   def __init__(self, methodName: str = "runTest") -> None:
      super(test_write_array_phase, self).__init__(methodName)
   
   def test(self):
      test_array = np.random.randint(64, size=(2, 16, 16))
      self.paa.initialize_antenna()
      self.paa.write_array_phase(test_array)

      for row in range(0, 8):
         for col in range(0, 8):         
            channels = my_utils.GROUP_CHANNEL[row][col]

            desc = channel_mapping.name_table[channels[0]]
            bus = desc['bus']
            chip_addr = desc['chip_addr']

            reg_val = self.paa.read_registers(bus, chip_addr, self.paa.REG_PS1, 2)
            ps1_reg = bitstring.Array('uint6', reg_val[0].to_bytes(3, 'big'))
            ps2_reg = bitstring.Array('uint6', reg_val[1].to_bytes(3, 'big'))

            for channel in channels:
               channel_num = channel_mapping.name_table[channel]['ch_num']
               if channel_num <= 4:
                  ps = int(ps1_reg[channel_num-1])
               else:   
                  ps = int(ps2_reg[channel_num-5])

               array_row, array_col = my_utils.to_cartesian(channel)
               array_index = 0 if channel[-1]  == 'H' else 1
               self.assertEqual(ps & 0x3f, int(test_array[array_index][array_row][array_col]) & 0x3f)   

if __name__ == '__main__':
   unittest.main()
