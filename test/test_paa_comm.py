import unittest
import random

import sys 
sys.path.append("..") 
import paa_control

class test_comm(unittest.TestCase):
   paa = paa_control.PAAControl('/dev/ttyUSB1', 'Receiving', 8) 

   def __init__(self, methodName: str = "runTest") -> None:
      super(test_comm, self).__init__(methodName)
   
   def test_all_bus_unicast_6_regs_addr0(self):
      test_data = {}
      for bus_num in range(0, 8):
         test_data[bus_num] = [[random.randint(0, 0xffffff) for j in range(6)] for i in range(8)]

      self.paa.write_register_burst(0x00, test_data)

      for bus_num in range(0, 8):
         for chip_addr in range(0, 8):
            chip_regs = self.paa.read_registers(bus_num, chip_addr, 0, 6)   
            self.assertEqual(chip_regs, test_data[bus_num][chip_addr])

   def test_all_bus_unicast_12_regs_addr0(self):
      test_data = {}
      for bus_num in range(0, 8):
         test_data[bus_num] = [[random.randint(0, 0xffffff) for j in range(12)] for i in range(8)]

      self.paa.write_register_burst(0x00, test_data)

      for bus_num in range(0, 8):
         for chip_addr in range(0, 8):
            chip_regs = self.paa.read_registers(bus_num, chip_addr, 0, 12)   
            self.assertEqual(chip_regs, test_data[bus_num][chip_addr])

   def test_all_bus_unicast_6_regs_addr40(self):
      test_data = {}
      for bus_num in range(0, 8):
         test_data[bus_num] = [[random.randint(0, 0xffffff) for j in range(6)] for i in range(8)]

      self.paa.write_register_burst(0x40, test_data)

      for bus_num in range(0, 8):
         for chip_addr in range(0, 8):
            chip_regs = self.paa.read_registers(bus_num, chip_addr, 0x40, 6)   
            self.assertEqual(chip_regs, test_data[bus_num][chip_addr])         

   def test_two_bus_unicast(self):
      test_data = {}
      for bus_num in range(0, 8):
         test_data[bus_num] = [[int(0)] for i in range(8)]   

      self.paa.write_register_burst(0x00, test_data)  
      
      test_data = {}
      for bus_num in range(0, 2):
         test_data[bus_num] = [[random.randint(0, 0xffffff)] for i in range(8)]     

      self.paa.write_register_burst(0x00, test_data)         

      for bus_num in range(0, 8):
         for chip_addr in range(0, 8):
            chip_regs = self.paa.read_registers(bus_num, chip_addr, 0x0, 1)   

            if bus_num < 2:
               self.assertEqual(chip_regs, test_data[bus_num][chip_addr])    
            else:
               self.assertEqual(chip_regs, [int(0)])    

   def test_all_bus_broadcast(self):
      test_data = {}
      for bus_num in range(0, 8):
         test_data[bus_num] = [[random.randint(0, 0xffffff) for i in range(12)]]         
        
      self.paa.write_register_burst(0x0, test_data, broadcast=True)         

      for bus_num in range(0, 8):
         for chip_addr in range(0, 8):
            chip_regs = self.paa.read_registers(bus_num, chip_addr, 0, 12)   
            self.assertEqual(chip_regs, test_data[bus_num][0])      
 
if __name__ == '__main__':
   unittest.main()
