import unittest

import sys 
sys.path.append("..") 
import paa_control
import channel_mapping

class test_enable_channel(unittest.TestCase):
   paa = paa_control.PAAControl('COM13', 'Receiving', 8) 

   def __init__(self, methodName: str = "runTest") -> None:
      super(test_enable_channel, self).__init__(methodName)
   
   def test_single_channle(self):
      channel_desc = channel_mapping.name_table['G11_A1H']
      bus = channel_desc['bus']
      addr = channel_desc['chip_addr']
      ch_num = channel_desc['ch_num']
   
      self.paa.enable_channel('G11_A1H', True)

      reg_value = self.paa.read_registers(bus, addr, self.paa.REG_RFEN, 1)[0]
      self.assertEqual(reg_value & (1 << (ch_num-1)), 0)

      self.paa.enable_channel('G11_A1H', False)

      reg_value = self.paa.read_registers(bus, addr, self.paa.REG_RFEN, 1)[0]
      self.assertEqual(reg_value & (1 << (ch_num-1)), 1 << (ch_num-1))

   def test_group(self):
      channel_desc = channel_mapping.name_table['G11_A1H']
      bus = channel_desc['bus']
      addr = channel_desc['chip_addr']

      self.paa.enable_channel('G11', True)
      reg_value = self.paa.read_registers(bus, addr, self.paa.REG_RFEN, 1)[0]
      self.assertEqual(reg_value, 0x0)

      self.paa.enable_channel('G11H', True)
      reg_value = self.paa.read_registers(bus, addr, self.paa.REG_RFEN, 1)[0]
      self.assertEqual(reg_value, ~(1 << 1 | 1 << 2 | 1 << 5 | 1 << 6 | 1 << 8) & 0x1ff)

      self.paa.enable_channel('G11V', True)
      reg_value = self.paa.read_registers(bus, addr, self.paa.REG_RFEN, 1)[0]
      self.assertEqual(reg_value, ~(1 << 0 | 1 << 3 | 1 << 4 | 1 << 7 | 1 << 8) & 0x1ff)

   def test_all(self):
      self.paa.enable_channel('ALL', True)
      for bus in range(8):
         for chip in range(8):
            reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
            self.assertEqual(reg_value, 0x0)

      self.paa.enable_channel('ALLH', True)
      for bus in range(8):
         for chip in range(8):
            reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
            self.assertEqual(reg_value, ~(1 << 1 | 1 << 2 | 1 << 5 | 1 << 6 | 1 << 8) & 0x1ff)  

      self.paa.enable_channel('ALLV', True)
      for bus in range(8):
         for chip in range(8):
            reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
            self.assertEqual(reg_value, ~(1 << 0 | 1 << 3 | 1 << 4 | 1 << 7 | 1 << 8) & 0x1ff)

      self.paa.enable_channel('ALL', False)
      for bus in range(8):
         for chip in range(8):
            reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
            self.assertEqual(reg_value, 0xff)                  

   def test_block(self):
      block_busnum = {'B1':[2, 3], 'B2':[0, 1], 'B3':[6, 7], 'B4':[4, 5]}

      self.paa.enable_channel('ALL', False)

      for block_name in block_busnum.keys():
         self.paa.enable_channel(block_name, True)
         for bus in block_busnum[block_name]:
            for chip in range(8):
               reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
               self.assertEqual(reg_value, 0x0)

      self.paa.enable_channel('ALL', False)

      for block_name in block_busnum.keys():
         self.paa.enable_channel(block_name + 'H', True)
         for bus in block_busnum[block_name]:
            for chip in range(8):
               reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
               self.assertEqual(reg_value, ~(1 << 1 | 1 << 2 | 1 << 5 | 1 << 6 | 1 << 8) & 0x1ff)    

      self.paa.enable_channel('ALL', False)
      
      for block_name in block_busnum.keys():
         self.paa.enable_channel(block_name + 'V', True)
         for bus in block_busnum[block_name]:
            for chip in range(8):
               reg_value = self.paa.read_registers(bus, chip, self.paa.REG_RFEN, 1)[0]
               self.assertEqual(reg_value, ~(1 << 0 | 1 << 3 | 1 << 4 | 1 << 7 | 1 << 8) & 0x1ff)              

if __name__ == '__main__':
   unittest.main()
