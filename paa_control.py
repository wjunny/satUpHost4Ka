import serial
import time
import bitstring
import math
import numpy as np
import itertools
import re
from enum import Enum

import initial_data_8165
import initial_data_8365
import channel_mapping   
import my_utils

lhcp_initial_phase = {'H':[int(0), int(31), int(31), int(0)], 'V':[int(15), int(15), int(47), int(47)]}
rhcp_initial_phase = {'H':[int(0), int(31), int(31), int(0)], 'V':[int(47), int(47), int(15), int(15)]}

Polar = Enum('Polar', ['HORI_LP', 'VERT_LP', 'LH_CP', 'RH_CP'])

class CommError(IOError):
   ERR_MISMATCH_LENGTH = 1
   ERR_CRC = 2
   ERR_TIMEOUT = 3
   ERR_WRONG_OPCODE = 4
   ERR_WRONG_HEADER = 5
   ERR_INVALID_FORMAT = 6

   def __init__(self, msg:str, err_code:int):
      super(CommError, self).__init__(msg)
      self.err_code = err_code

class PAAControl():
   LUT_ADDR = 0x00
   REG_PS1 = 0x40
   REG_PS2 = 0x41
   REG_GC1 = 0x42
   REG_GC2 = 0x43
   REG_GC3 = 0x44
   REG_GC4 = 0x45
   REG_BIAS1 = 0x46
   REG_BIAS2 = 0x47
   REG_BIAS3 = 0x48
   REG_BIAS4 = 0x49
   REG_TCR = 0x4a
   REG_RFEN = 0x4b
   REG_LDO = 0x4c
   REG_ADC = 0x4d
   REG_PDS = 0x4e
   REG_ADCDAT = 0x52

   COMM_INTERVAL = 0.001

   def __init__(self, serial_device:str, paa_type:str, ant_addr:int):
      if paa_type == 'Transmitting':
         self.beamformer_number = '8165'
      elif paa_type == 'Receiving':  
         self.beamformer_number = '8365' 
      else:
         raise ValueError('Invalid PAA Type')   
      
      if self.beamformer_number == '8165':
         self.initial_data = initial_data_8165.initial_data
         self.lut = initial_data_8165.lut
         self.gain_lut = initial_data_8165.gain_lut
      else:
         self.initial_data = initial_data_8365.initial_data
         self.lut = initial_data_8365.lut
         self.gain_lut = initial_data_8365.gain_lut   

      try:
         self.serial_port = serial.Serial(serial_device, 115200, timeout=0.5)
         self.serial_port.reset_input_buffer()
         self.serial_port.reset_output_buffer()   
         while True:
            data = self.serial_port.read()
            if len(data) == 0:
               break
      except serial.SerialException as e:
         print(str(e))      
 
      self.array_phase_shift = np.zeros((2, 16, 16), dtype=int) # (0, 16, 16) hori channels, (1, 16, 16) vert channels

      self.ant_addr = ant_addr
      if ant_addr < 0x01 or ant_addr > 0x08:
         raise ValueError('Invalid Antenna Address')

   def get_serial_port(self):
      return self.serial_port

   def recv_response(self, op_code:int, length:int):
      frame = self.serial_port.read(length)
      if len(frame) != length:
         raise CommError('Response length mismatch {:d}'.format(len(frame)), CommError.ERR_MISMATCH_LENGTH)

      if frame[0] != 0xff:
         raise CommError('Wrong header', CommError.ERR_WRONG_HEADER)
                         
      if frame[2] != op_code:
         raise CommError('Wrong opcode', CommError.ERR_WRONG_OPCODE)
      
      crc16 = my_utils.calc_crc(frame[1:-2])
      recv_crc16 = int.from_bytes(frame[-2:], byteorder='big', signed=False)
      if crc16 != recv_crc16:
         raise CommError('CRC Error', CommError.ERR_CRC)

      return list(frame[5:-2])
      
   def write_registers(self, bus:int, chip_addr:int, reg_addr:int, data:list):
      if (bus < 0x00 or bus > 0x07) and bus != 0xff:
         raise ValueError('Invalid Bus Address')
      if (chip_addr < 0x00 or chip_addr > 0x07) and chip_addr != 0xff:
         raise ValueError('Invalid Chip Address')

      payload_length = int(len(data)*3 + 4)
      frame_length = payload_length + 5 + 2

      cmd = [int(0)]*frame_length
      cmd[0] = 0xff
      cmd[1] = self.ant_addr
      cmd[2] = 0x02
      cmd[3] = payload_length.to_bytes(2, 'big')[0]
      cmd[4] = payload_length.to_bytes(2, 'big')[1]
      cmd[5] = bus
      cmd[6] = chip_addr
      cmd[7] = reg_addr
      cmd[8] = len(data)

      cmd[9:-2] = [y for x in data for y in x.to_bytes(3, 'big')]

      crc16 = my_utils.calc_crc(cmd[1:-2])
      cmd[-2:] = crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()

      self.serial_port.write(cmd)
      length = 5 + 2 + 2
      resp_data = self.recv_response(0x02, length)
    
      time.sleep(self.COMM_INTERVAL)

   def write_register_burst(self, reg_addr:int, reg_data:dict, broadcast:bool=False):
      reg_data = dict(sorted(reg_data.items()))

      data_buffer = []
      bus_mask = int(0)
      
      for bus_num in reg_data.keys():
         if bus_num < 0 or bus_num > 7:
            raise ValueError('Invalid Bus Number')
         if broadcast and len(reg_data[bus_num]) != 1:
            raise ValueError('Invalid Number Of Broadcast Data Blocks')
         if not broadcast and len(reg_data[bus_num]) != 8:
            raise ValueError('Invalid Number of Unicast Data Blocks')
         
         bus_mask |= (1 << bus_num)

         tmp_array = np.array(reg_data[bus_num])
         rows, cols = tmp_array.shape
         if cols > 12:
            raise ValueError('Invalid Number of Registers')

         data_buffer += list(itertools.chain.from_iterable(reg_data[bus_num]))   

      bytes_buffer = [y for x in data_buffer for y in x.to_bytes(3, 'big')]   

      payload_length = int(len(bytes_buffer) + 4)

      cmd = [int]*9
      cmd[0] = 0xff   
      cmd[1] = self.ant_addr
      cmd[2] = 0x09
      cmd[3] = payload_length.to_bytes(2, 'big')[0]
      cmd[4] = payload_length.to_bytes(2, 'big')[1]
      cmd[5] =  bus_mask
      cmd[6] = reg_addr
      cmd[7] = cols
      cmd[8] = 0xff if broadcast else 0x00
      cmd += bytes_buffer

      crc16 = my_utils.calc_crc(cmd[1:])
      cmd += crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()

      self.serial_port.write(cmd)
      length = 5 + 1 + 2
      resp_data = self.recv_response(0x09, length)
      if resp_data[0] == 0xff:
         raise CommError('Invalid Format', CommError.ERR_INVALID_FORMAT)
    
      time.sleep(self.COMM_INTERVAL)

   def read_registers(self, bus:int, chip_addr:int, reg_addr:int, length:int) -> list:
      if bus < 0x00 or bus > 0x07:
         raise ValueError('Invalid Bus Address')
      if chip_addr < 0x00 or chip_addr > 0x07:
         raise ValueError('Invalid Chip Address')
   
      cmd = [int(0)]*11
      cmd[0] = 0xff
      cmd[1] = self.ant_addr
      cmd[2] = 0x01
      cmd[3] = int(4).to_bytes(2, 'big')[0]
      cmd[4] = int(4).to_bytes(2, 'big')[1]
      cmd[5] = bus
      cmd[6] = chip_addr
      cmd[7] = reg_addr
      cmd[8] = length
      crc16 = my_utils.calc_crc(cmd[1:-2])
      cmd[-2:] = crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()
      
      self.serial_port.write(cmd)
      length = 5 + 1 + length*3 + 2
      resp = self.recv_response(0x01, length)      
      resp = resp[1:]

      reg_data = [int.from_bytes(resp[i:i+3], byteorder='big', signed=False) for i in range(0, len(resp), 3)]

      time.sleep(self.COMM_INTERVAL)
      return reg_data      
    
   def enable_amplifier(self, enable:bool):
      cmd = [int(0)]*8
      cmd[0] = 0xff
      cmd[1] = self.ant_addr
      cmd[2] = 0x03
      cmd[3] = int(1).to_bytes(2, 'big')[0]
      cmd[4] = int(1).to_bytes(2, 'big')[1]
      cmd[5] = 0xff if enable else 0x00
      crc16 = my_utils.calc_crc(cmd[1:-2])
      cmd[-2:] = crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()
      
      self.serial_port.write(cmd)
      length = 5 + 1 + 2
      resp = self.recv_response(0x03, length)
      
      time.sleep(self.COMM_INTERVAL)

   def load_control(self):
      cmd = [int(0)]*7
      cmd[0] = 0xff
      cmd[1] = self.ant_addr
      cmd[2] = 0x04
      cmd[3] = 0
      cmd[4] = 0
      crc16 = my_utils.calc_crc(cmd[1:-2])
      cmd[-2:] = crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()

      self.serial_port.write(cmd)
      length = 5 + 2
      resp_data = self.recv_response(0x04, length)
      
      time.sleep(self.COMM_INTERVAL)
   
   def initialize_antenna(self):
      self.write_registers(0xff, 0xff, 0, self.lut + self.initial_data) #bus = 0xff, parallel write mode. chip addr = 0xff, broadcast mode.

   def enable_channel(self, channel_name:str, enable:bool):
      chn = channel_name.upper()

      if re.match('^G[1-8][1-8]_A[1-4][HV]$', chn):
         ch_desc = channel_mapping.name_table[chn]
         bus = ch_desc['bus']
         addr = ch_desc['chip_addr']
         ch_num = ch_desc['ch_num']

         reg_value = self.read_registers(bus, addr, self.REG_RFEN, 1)[0]

         if enable:
            reg_value &= ~(1 << (ch_num - 1))
         else:
            reg_value |= 1 << (ch_num - 1)

         self.write_registers(bus, addr, self.REG_RFEN, [reg_value])
         return

      if chn == 'ALL' and not enable:
         data_block = {}
         for bus_num in range(0, 8):
            data_block[bus_num] = [[0x0ff]]         

         self.write_register_burst(self.REG_RFEN, data_block, broadcast=True)     
         return

      if (chn == 'ALL' or chn == 'ALLH' or chn == 'ALLV') and enable:
         reg_value = 0x0
         if chn == 'ALL':
            pass
         elif chn == 'ALLH':
            reg_value |= ~(1 << 1 | 1 << 2 | 1 << 5 | 1 << 6) & 0xff
         else:
            reg_value |= ~(1 << 0 | 1 << 3 | 1 << 4 | 1 << 7) & 0xff

         data_block = {}
         for bus_num in range(0, 8):
            data_block[bus_num] = [[reg_value]]         

         self.write_register_burst(self.REG_RFEN, data_block, broadcast=True)     
         return
      
      if re.match('^B[1-4](H|V|)$', chn) and enable:
         reg_value = 0x0

         if chn[-1] == 'H':
            reg_value |= ~(1 << 1 | 1 << 2 | 1 << 5 | 1 << 6) & 0xff
         elif chn[-1] == 'V':
            reg_value |= ~(1 << 0 | 1 << 3 | 1 << 4| 1 << 7) & 0xff

         data_block = {}
         if chn[1] == '1':
            data_block[2] = [[reg_value]]
            data_block[3] = [[reg_value]]
         elif chn[1] == '2':
            data_block[0] = [[reg_value]]
            data_block[1] = [[reg_value]]
         elif chn[1] == '3':
            data_block[6] = [[reg_value]]
            data_block[7] = [[reg_value]]
         else:
            data_block[4] = [[reg_value]]
            data_block[5] = [[reg_value]]

         self.write_register_burst(self.REG_RFEN, data_block, broadcast=True)     
         return   
      
      if re.match('^G[1-8][1-8](H|V|)$', chn) and enable:
         reg_value = 0x0
         
         if chn[-1] == 'H':
            reg_value |= ~(1 << 1 | 1 << 2 | 1 << 5 | 1 << 6) & 0xff
         elif chn[-1] == 'V':
            reg_value |= ~(1 << 0 | 1 << 3 | 1 << 4 | 1 << 7) & 0xff

         ch_desc = channel_mapping.name_table[chn[0:3]+'_A1H']
         bus = ch_desc['bus']
         addr = ch_desc['chip_addr']

         self.write_registers(bus, addr, self.REG_RFEN, [reg_value])
         return       
      
   def set_phase(self, channel_name:str, phase:int):
      ch_desc = channel_mapping.name_table[channel_name.upper()]
      bus = ch_desc['bus']
      chip_addr = ch_desc['chip_addr']
      ch_num = ch_desc['ch_num']

      regaddr = self.REG_PS1 if ch_num < 5 else self.REG_PS2
      regval = self.read_registers(bus, chip_addr, regaddr, 1)[0]
      regval_array  = bitstring.Array('uint6', regval.to_bytes(3, 'big'))
     
      ch_num = ch_num - 5 if ch_num > 4 else ch_num - 1
      regval_array[ch_num] = phase & 0x3f

      regval = int.from_bytes(regval_array.tobytes(), 'big')
      self.write_registers(bus, chip_addr, regaddr, [regval])

   def set_gain(self, channel_name:str, gain:str):
      ch_desc = channel_mapping.name_table[channel_name.upper()]
      bus = ch_desc['bus']
      chipaddr = ch_desc['chip_addr']
      ch_num = ch_desc['ch_num']

      if ch_num <= 2:
         regaddr = self.REG_GC1
         bit_index = 14 if ch_num == 1 else 4
      elif ch_num <= 4:
         regaddr = self.REG_GC2
         bit_index = 14 if ch_num == 3 else 4
      elif ch_num <= 6:
         regaddr = self.REG_GC3
         bit_index = 14 if ch_num == 5 else 4
      else:
         regaddr = self.REG_GC4     
         bit_index = 14 if ch_num == 7 else 4

      regval = self.read_registers(bus, chipaddr, regaddr, 1)[0]    
      val_bits = bitstring.BitStream(regval.to_bytes(3, 'big'))
      val_bits[bit_index:bit_index+10] = self.gain_lut[gain]
      regval = int.from_bytes(val_bits.tobytes(), 'big')
      
      self.write_registers(bus, chipaddr, regaddr, [regval])

   def group_phase_gain(self, group_names:str, polar:Enum, calib:dict=None, phase_offset:float=0.0, gain_offset:float=0.0):
      ps1 = bitstring.Array('uint6', [0, 0, 0, 0])
      ps2 = bitstring.Array('uint6', [0, 0, 0, 0])
      gain1 = bitstring.Array('uint10', [0x0, 0x0, 0x3ff, 0x3ff])
      gain2 = bitstring.Array('uint10', [0x0, 0x0, 0x3ff, 0x3ff])
      gain3 = bitstring.Array('uint10', [0x0, 0x0, 0x3ff, 0x3ff])
      gain4 = bitstring.Array('uint10', [0x0, 0x0, 0x3ff, 0x3ff])

      for name in group_names:
         desc = channel_mapping.name_table[name]
         channel = desc['ch_num']
         
         if polar == Polar.HORI_LP or polar == Polar.VERT_LP:
            v = int(31) if my_utils.is_inverting_channel(name) else (0)
         elif polar == Polar.LH_CP or polar == Polar.RH_CP:
            cpps = lhcp_initial_phase if polar == Polar.LH_CP else rhcp_initial_phase
            v = cpps[name[-1]][my_utils.channel_to_index(name)]
         else:
            raise ValueError('Invalid polarization setting')
         
         if calib is not None and name in calib:
            v += my_utils.phase_to_index(calib[name]['phase'])

         v += my_utils.phase_to_index(phase_offset)
         v = my_utils.wrap_phase_index(v)   

         if polar == Polar.LH_CP or polar == Polar.RH_CP:
            array_row, array_col = my_utils.to_cartesian(name)   
            if name[-1] == 'H':
               self.array_phase_shift[0][array_row][array_col] = v
            else:
               self.array_phase_shift[1][array_row][array_col] = v

         if channel <= 4:
            ps1[channel-1] = v & 0x3f
         else:
            ps2[channel-5] = v & 0x3f
    
         gain = gain_offset
         if calib is not None and name in calib: 
            gain += calib[name]['gain']

         gain_reg_val = self.gain_lut[my_utils.db_to_str(gain)]   

         if channel <= 2:
            gain1[4-channel] = gain_reg_val
         elif channel <= 4:
            gain2[6-channel] = gain_reg_val
         elif channel <= 6:
            gain3[8-channel] = gain_reg_val
         else:
            gain4[10-channel] = gain_reg_val

      reg_ps1 = int.from_bytes(ps1.tobytes(), 'big')
      reg_ps2 = int.from_bytes(ps2.tobytes(), 'big')
      reg_gain1 = int.from_bytes(gain1.tobytes(), 'big') & 0xffffff
      reg_gain2 = int.from_bytes(gain2.tobytes(), 'big') & 0xffffff
      reg_gain3 = int.from_bytes(gain3.tobytes(), 'big') & 0xffffff
      reg_gain4 = int.from_bytes(gain4.tobytes(), 'big') & 0xffffff

      return [reg_ps1, reg_ps2, reg_gain1, reg_gain2, reg_gain3, reg_gain4]
         
   def set_polarization(self, scope:str, polar:Enum, calib:dict=None, phase_offset:float=0.0, gain_offset:float=0.0, active_channel:bool=True):
      _scope = scope.upper()
      
      if active_channel:
         self.enable_channel('ALL', False)

      is_chunk = False
      
      if re.match('^G[1-8][1-8]$', _scope):
         channel_names = my_utils.GROUP_CHANNEL[int(_scope[1])-1][int(_scope[2])-1]
         registers = self.group_phase_gain(channel_names, polar, calib, phase_offset, gain_offset)

         desc = channel_mapping.name_table[_scope[0:3] + '_A1H']
         bus = desc['bus']
         chipaddr = desc['chip_addr']

         self.write_registers(bus, chipaddr, self.REG_PS1, registers)
      elif re.match('^C[1-4][1-4]$', _scope):
         is_chunk = True
         chunk = my_utils.CHUNKS[int(_scope[1])-1][int(_scope[2])-1]
         for group in chunk:
            group_name = 'G{}{}'.format(group[0], group[1])
            self.set_polarization(group_name, polar, calib, phase_offset, gain_offset, active_channel=False)
      elif re.match('^B[1-4]$', _scope):
         block = my_utils.ALL_BLOCKS[int(_scope[1]) - 1]

         register_data = {}
         for block_bus in block:
            register_data[block_bus['bus']] = [
               self.group_phase_gain(my_utils.GROUP_CHANNEL[g[0]-1][g[1]-1], polar, calib, phase_offset, gain_offset) for g in block_bus['groups']]         
              
         self.write_register_burst(self.REG_PS1, register_data)   
      elif _scope == 'ALL':
         register_data = {}
         for block in my_utils.ALL_BLOCKS:
            for block_bus in block:
               register_data[block_bus['bus']] = [
                  self.group_phase_gain(my_utils.GROUP_CHANNEL[g[0]-1][g[1]-1], polar, calib, phase_offset, gain_offset) for g in block_bus['groups']]         

         self.write_register_burst(self.REG_PS1, register_data)   
      else:
         raise ValueError('Invalid scope name')

      self.load_control()   

      if active_channel:
         if not is_chunk:
            channels = _scope
            if polar == Polar.HORI_LP:
               channels = _scope + 'H'
            elif polar == Polar.VERT_LP:
               channels = _scope + 'V'

            self.enable_channel(channels, True)
         else:
            for group in chunk: 
               group_name = 'G{}{}'.format(group[0], group[1])
               if polar == Polar.HORI_LP:
                  group_name += 'H'
               elif polar == Polar.VERT_LP:
                  group_name += 'V'
               self.enable_channel(group_name, True)

   def write_array_phase(self, phases:np.ndarray):
      registers_data = {}

      for block in my_utils.ALL_BLOCKS:
         for block_bus in block:
            bus_num = block_bus['bus']
            registers_data[bus_num] = []

            for group in block_bus['groups']:
               channels = my_utils.GROUP_CHANNEL_H[group[0]-1][group[1]-1]
               ps1_reg = bitstring.Array('uint6', [0, 0, 0, 0])
               ps2_reg = bitstring.Array('uint6', [0, 0, 0, 0])

               for ch in channels:
                  array_row, array_col = my_utils.to_cartesian(ch)
                  psval_h = phases[0][array_row][array_col]
                  psval_v = phases[1][array_row][array_col]

                  ch = ch[:-1]   
                  chnum_h = channel_mapping.name_table[ch+'H']['ch_num']
                  chnum_v = channel_mapping.name_table[ch+'V']['ch_num']

                  if chnum_h <= 4:
                     ps1_reg[chnum_h-1] = int(psval_h & 0x3f)
                  else:
                     ps2_reg[chnum_h-5] = int(psval_h & 0x3f)

                  if chnum_v <= 4:
                     ps1_reg[chnum_v-1] = int(psval_v & 0x3f)
                  else:
                     ps2_reg[chnum_v-5] = int(psval_v & 0x3f)

               registers_data[bus_num].append(
                  [int.from_bytes(ps1_reg.tobytes(), 'big'), int.from_bytes(ps2_reg.tobytes(), 'big')])  

      self.write_register_burst(self.REG_PS1, registers_data)
      self.load_control()      

   def steer_beam(self, azi_angle:float=0.0, ele_angle:float=0.0):
      m_phases = np.zeros((2, 16, 16), dtype=int)

      angle = my_utils.wrap360(azi_angle) #deg
      phi = my_utils.wrap360(math.degrees(math.pi * math.sin(math.radians(angle))))
      phi_index = my_utils.phase_to_index(phi)
    
      m_theta =  np.tile(np.arange(16, dtype=int), (16, 1)) 
      m_theta *= phi_index
     
      m_phases[0] = (self.array_phase_shift[0] + m_theta) % 64
      m_phases[1] = (self.array_phase_shift[1] + m_theta) % 64

      angle = my_utils.wrap360(ele_angle) #deg
      phi = my_utils.wrap360(math.degrees(math.pi * math.sin(math.radians(angle))))
      phi_index = my_utils.phase_to_index(phi)
    
      m_theta =  np.tile(np.arange(16, dtype=int), (16, 1)) 
      m_theta = m_theta.T
      m_theta *= phi_index

      m_phases[0] = (m_phases[0] + m_theta) % 64
      m_phases[1] = (m_phases[1] + m_theta) % 64

      self.write_array_phase(m_phases)

   def pmic_status(self):
      cmd = [int(0)]*7
      cmd[0] = 0xff
      cmd[1] = self.ant_addr
      cmd[2] = 0x05
      cmd[3] = 0
      cmd[4] = 0
      crc16 = my_utils.calc_crc(cmd[1:-2])
      cmd[-2:] = crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()

      self.serial_port.write(cmd)
      length = 5 + 14 + 2
      resp = self.recv_response(0x05, length)

      vin_raw = int.from_bytes(resp[0:2], byteorder='big', signed=False)
      iin_raw = int.from_bytes(resp[2:4], byteorder='big', signed=False)
      vout_raw = int.from_bytes(resp[4:6], byteorder='big', signed=False)
      iout_raw = int.from_bytes(resp[6:8], byteorder='big', signed=False)
      temp_raw = int.from_bytes(resp[8:10], byteorder='big', signed=False)
      pout_raw = int.from_bytes(resp[10:12], byteorder='big', signed=False)
      status_word = int.from_bytes(resp[12:14], byteorder='big', signed=False)

      time.sleep(self.COMM_INTERVAL)

      return {'vin': float(vin_raw&0x7ff)*0.25, 'iin': float(iin_raw&0x7ff)*0.25, 'vout': float(vout_raw&0xfff)*0.001, 'iout': float(iout_raw&0x7ff), \
              'temp': float(temp_raw&0xff), 'pout': float(pout_raw&0x7ff), 'status_word': status_word}
   
   def power_on(self, enable:bool):
      cmd = [int(0)]*8
      cmd[0] = 0xff
      cmd[1] = self.ant_addr
      cmd[2] = 0x06
      cmd[3] = int(1).to_bytes(2, 'big')[0]
      cmd[4] = int(1).to_bytes(2, 'big')[1]
      cmd[5] = 0xff if enable else 0x00
      crc16 = my_utils.calc_crc(cmd[1:-2])
      cmd[-2:] = crc16.to_bytes(2, 'big')

      self.serial_port.reset_input_buffer()
      self.serial_port.write(cmd)
      length = 5 + 1 + 2
      resp = self.recv_response(0x06, length)
      
      time.sleep(self.COMM_INTERVAL)
