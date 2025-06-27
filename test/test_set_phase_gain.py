import unittest

import sys 
sys.path.append("..") 
import paa_control
import channel_mapping
import initial_data_8365

class test_set_phase_gain(unittest.TestCase):
   paa = paa_control.PAAControl('COM13', 'Receiving', 8) 

   def __init__(self, methodName: str = "runTest") -> None:
      super(test_set_phase_gain, self).__init__(methodName)
   
   def test_set_phase(self):
      self.paa.set_phase('G11_A1H', 0b101010)

      channel_desc = channel_mapping.name_table['G11_A1H']
      bus = channel_desc['bus']
      chip_addr = channel_desc['chip_addr']
      channel = channel_desc['ch_num']
   
      reg_addr = self.paa.REG_PS1 if channel <= 4 else self.paa.REG_PS2

      reg_val = self.paa.read_registers(bus, chip_addr, reg_addr, 1)[0]

      bit_shift = (int(4) - channel)*int(6) if channel <= 4 else (int(8) - channel)*int(6)
      self.assertEqual((reg_val >> bit_shift)&0x3f, 0b101010)

   def test_set_gain(self):   
      self.paa.set_gain('G11_A1H', '-13')

      channel_desc = channel_mapping.name_table['G11_A1H']
      bus = channel_desc['bus']
      chip_addr = channel_desc['chip_addr']
      channel = channel_desc['ch_num']

      if channel <= 2:
         reg_addr = self.paa.REG_GC1
      elif channel <= 4:
         reg_addr = self.paa.REG_GC2
      elif channel <= 6:
         reg_addr = self.paa.REG_GC3
      else:
         reg_addr = self.paa.REG_GC4

      reg_val = self.paa.read_registers(bus, chip_addr, reg_addr, 1)[0]

      bit_shift = 10 if channel % 2 == 0 else 0
      self.assertEqual((reg_val >> bit_shift)&0x3ff, initial_data_8365.gain_lut['-13'])

if __name__ == '__main__':
   unittest.main()
