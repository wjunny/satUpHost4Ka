import unittest

import sys 
sys.path.append("..") 
import paa_control
import channel_mapping
import my_utils

class test_set_polar(unittest.TestCase):
   paa = paa_control.PAAControl('COM13', 'Receiving', 8) 

   def __init__(self, methodName: str = "runTest") -> None:
      super(test_set_polar, self).__init__(methodName)

   def test_group(self):
      channel_desc = channel_mapping.name_table['G11_A1H']
      bus = channel_desc['bus']
      chip_addr = channel_desc['chip_addr']

      self.paa.initialize_antenna()
      self.paa.set_polarization('G11', paa_control.Polar.HORI_LP, gain_offset=-1.0)

      register = self.paa.read_registers(bus, chip_addr, self.paa.REG_PS1, 2)
      self.assertEqual(register, [(0 << 18) | (31 << 12) | (31 << 6) | 31, (31 << 18) | (0 << 12) | (0 << 6) | 0]) 

      register = self.paa.read_registers(bus, chip_addr, self.paa.REG_GC1, 4)
      self.assertEqual(register, [(0x0003dd << 10) | 0x3dd, (0x0003dd << 10) | 0x3dd, (0x0003dd << 10) | 0x3dd, (0x0003dd << 10) | 0x3dd])

      self.paa.initialize_antenna()
      self.paa.set_polarization('G11', paa_control.Polar.LH_CP)

      register = self.paa.read_registers(bus, chip_addr, self.paa.REG_PS1, 2)
      self.assertEqual(register, [(16 << 18) | (32 << 12) | (32 << 6) | 48, (48 << 18) | (0 << 12) | (0 << 6) | 16]) 

      channel_desc = channel_mapping.name_table['G21_A1H']
      bus = channel_desc['bus']
      chip_addr = channel_desc['chip_addr']

      self.paa.initialize_antenna()
      self.paa.set_polarization('G21', paa_control.Polar.HORI_LP)

      register = self.paa.read_registers(bus, chip_addr, self.paa.REG_PS1, 2)
      self.assertEqual(register, [(31 << 18) | (0 << 12) | (0 << 6) | 0, (0 << 18) | (31 << 12) | (31 << 6) | 31]) 

      self.paa.initialize_antenna()
      self.paa.set_polarization('G21', paa_control.Polar.LH_CP)

      register = self.paa.read_registers(bus, chip_addr, self.paa.REG_PS1, 2)
      self.assertEqual(register, [(48 << 18) | (0 << 12) | (0 << 6) | 16, (16 << 18) | (32 << 12) | (32 << 6) | 48]) 
     
   def test_block(self):
      self.paa.initialize_antenna()
      self.paa.set_polarization('B1', paa_control.Polar.HORI_LP)

      for bus in my_utils.BLOCK1:
         bus_num = bus['bus']
         for addr in range(0, 8):
            register = self.paa.read_registers(bus_num, addr, self.paa.REG_PS1, 2)
            row = bus['groups'][addr][0]
            if row % 2 == 0:
               self.assertEqual(register, [(31 << 18) | (0 << 12) | (0 << 6) | 0, (0 << 18) | (31 << 12) | (31 << 6) | 31])    
            else:
               self.assertEqual(register, [(0 << 18) | (31 << 12) | (31 << 6) | 31, (31 << 18) | (0 << 12) | (0 << 6) | 0]) 

   def test_entire_lp(self):
      self.paa.initialize_antenna()
      self.paa.set_polarization('ALL', paa_control.Polar.HORI_LP)

      for block in my_utils.ALL_BLOCKS:
         for bus in block:
            bus_num = bus['bus']
            for addr in range(0, 8):
               register = self.paa.read_registers(bus_num, addr, self.paa.REG_PS1, 2)
               row = bus['groups'][addr][0]
               if row % 2 == 0:
                  self.assertEqual(register, [(31 << 18) | (0 << 12) | (0 << 6) | 0, (0 << 18) | (31 << 12) | (31 << 6) | 31])    
               else:
                  self.assertEqual(register, [(0 << 18) | (31 << 12) | (31 << 6) | 31, (31 << 18) | (0 << 12) | (0 << 6) | 0]) 


if __name__ == '__main__':
   unittest.main()
