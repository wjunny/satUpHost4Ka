import argparse
import time
import yaml

import paa_control

def check_registers(paa:paa_control.PAAControl):
   for bus in range(0, 8):
      for chip in range(0, 8):
         length  = int(79) if paa.beamformer_number == '8165' else int(78)
         read_buffer = paa.read_registers(bus, chip, 0, length)
         if read_buffer is None:
            print('read bus{} chip{} error'.format(bus, chip))
            return

         for i in range(0, 64):
            if read_buffer[i] != paa.lut[i]:
               print('bus{} chip{} addr 0x{:02x} error, val=0x{:06x} actual=0x{:06x}'.format(bus, chip, i, read_buffer[i], paa.lut[i]))
               return

         for i in range(0, length-64):
            if read_buffer[64+i] != paa.initial_data[i]:
               print('bus{} chip{} addr 0x{:02x} error, val=0x{:06x} actual=0x{:06x}'.format(bus, chip, 64+i, read_buffer[64+i], paa.initial_data[i]))
               return   

         #time.sleep(0.1)      

   print('All registers are correct')      

def print_registers(addr, regs):
   length = len(regs)

   if (length%4) != 0:
      for i in range(0, 4-(length%4)):
         regs.append(0)

   for i in range(0, int(len(regs)/4)):
      print('0x{:02x}: {}'.format(addr+4*i, ' '.join('0x{:06x}'.format(x) for x in regs[i*4:i*4+4])))

   print('') 

def print_all_registers(paa:paa_control.PAAControl):
   for bus in range(0, 8):
      for chip in range(0, 8):
         print('bus{},chip{}'.format(bus, chip))
         length  = int(79) if paa.beamformer_number == '8165' else int(78)
         regs = paa.read_registers(bus, chip, 0, length)
         print_registers(0, regs)

def read_chip_voltage_temp(paa:paa_control.PAAControl, bus:int, chip_addr:int, type:str):
   if type == 'voltage':
      paa.write_registers(bus, chip_addr, paa.REG_ADC, [0x000201])                
   elif type == 'temp':
      paa.write_registers(bus, chip_addr, paa.REG_ADC, [0x000101])      
   else:
      raise ValueError('type must be voltage or temp')

   read_value = int(0)

   for i in range(100):
      read_value = paa.read_registers(bus, chip_addr, paa.REG_ADCDAT, 1)[0]

   read_value = paa.read_registers(bus, chip_addr, paa.REG_ADCDAT, 1)[0]

   if type == 'voltage':      
      print('bus{} chip{} voltage={:2.3f}V'.format(bus, chip_addr, float(read_value&0xff)/256*2.5))   
   else:
      read_value &= 0xff
      temp = float(0)

      if read_value > 90:
         temp = -50.0
      elif read_value < 71:
         temp = 110.0
      else:
         temp_table = {90:-50, 89:-45, 88:-37, 87:-30, 86:-22, 85:-15, 84:-7, 83:2, 82:10, 81:17, 80:27, 79:37, 78:47, 77:57, 76:65, 75:72, 74:82, 73:92, 72:102, 71:110}
         temp = temp_table[read_value] 

      print('bus{} chip{} value={} temp={}'.format(bus, chip_addr, read_value, temp))      

def read_chip_power(paa:paa_control.PAAControl, bus:int, chip_addr:int):
   paa.write_registers(bus, chip_addr, paa.REG_ADC, [0x000401])   

   pdv = []

   for ch in range(0, 8):
      paa.write_registers(bus, chip_addr, paa.REG_PDS, [ch])   

      read_value = int(0)
      for i in range(100):
         read_value = paa.read_registers(bus, chip_addr, paa.REG_ADCDAT, 1)[0]

      read_value = paa.read_registers(bus, chip_addr, paa.REG_ADCDAT, 1)[0]
      pdv.append(read_value&0xff)

      print('bus{} chip{} power=[{}]'.format(bus, chip_addr, ' '.join('{}'.format(x) for x in pdv)))        

def process_command_line():
   parser = argparse.ArgumentParser()
   parser.add_argument('--device', nargs=1, required=True)
   parser.add_argument('--type', nargs=1, required=True, choices=('tx', 'rx'))
   parser.add_argument('--ant_addr', nargs=1, required=True)
   parser.add_argument('--enable', action='store_true')
   parser.add_argument('--disable', action='store_true')
   parser.add_argument('--read_all', action='store_true')
   parser.add_argument('--load', action='store_true')
   parser.add_argument('--init', action='store_true')
   parser.add_argument('--check', action='store_true')
   parser.add_argument('--voltage', nargs=2, metavar=('BUS', 'CHIP'))
   parser.add_argument('--temp', nargs=2, metavar=('BUS', 'CHIP'))
   parser.add_argument('--power', nargs=2, metavar=('BUS', 'CHIP'))
   parser.add_argument('--test', action='store_true')
   parser.add_argument('--write', nargs=4, metavar=('BUS', 'CHIP', 'REG_ADDR', 'VAL'))
   parser.add_argument('--read', nargs=3,  metavar=('BUS', 'CHIP', 'REG_ADDR'))
   parser.add_argument('--pmic', action='store_true')
   parser.add_argument('--power_on', action='store_true')
   parser.add_argument('--power_off', action='store_true')
   parser.add_argument('--enable_channel', nargs=2, metavar=('ALL|ALLH|ALLV|GROUP|BLOCK|CHN_NAME', 'ENABLE|DISABLE'))
   parser.add_argument('--set_phase', nargs=2, metavar=('CHANNEL_NAME', 'PHASE'))
   parser.add_argument('--set_gain', nargs=2, metavar=('CHANNEL_NAME', 'GAIN'))
   parser.add_argument('--steer_beam', nargs=3, metavar=('DIR', 'ANGLE', 'AXES'))
   parser.add_argument('--set_lp', nargs=2, metavar=('ALL|GROUP|CHUNK|BLOCK', 'DIR'))
   parser.add_argument('--set_cp', nargs=2, metavar=('ALL|GROUP|CHUNK|BLOCK', 'DIR'))
   parser.add_argument('--calib', type=str, metavar=('CALIB_FILE'))

   args = parser.parse_args()
  
   paa_type = 'Transmitting' if args.type[0] == 'tx' else 'Receiving'
   ant_addr = int(args.ant_addr[0])

   print('PAA Type: ' + paa_type + '\n')
   antenna = paa_control.PAAControl(args.device[0], paa_type, ant_addr)

   if args.write:
      antenna.write_registers(int(args.write[0], 16), int(args.write[1], 16), int(args.write[2], 16), [int(args.write[3], 16)])

   if args.read:
      reg_data = antenna.read_registers(int(args.read[0], 16), int(args.read[1], 16), int(args.read[2], 16), 1)
      print('0x{:02x}: 0x{:06x}'.format(int(args.read[2], 16), reg_data[0]))

   if args.enable:
      antenna.enable_amplifier(True)

   if args.disable:
      antenna.enable_amplifier(False)

   if args.load:
      antenna.load_control()

   if args.read_all:
      print_all_registers(antenna)

   if args.init:
      antenna.initialize_antenna()

   if args.check:
      check_registers(antenna)

   if args.voltage:
      read_chip_voltage_temp(antenna, int(args.voltage[0]), int(args.voltage[1]), 'voltage')

   if args.temp:
      read_chip_voltage_temp(antenna, int(args.temp[0]), int(args.temp[1]), 'temp')   

   if args.power:
      if paa_type == 'Transmitting':
         read_chip_power(antenna, int(args.power[0]), int(args.power[1])) 

   if args.test:
      for bus in range(0, 8):
         for chip in range(0, 8):
            v = int((bus << 4) + chip)
            antenna.write_registers(bus, chip, antenna.LUT_ADDR, [v])  
            print('Write 0x{:02x} to bus {} chip {}'.format(v, bus, chip))

      time.sleep(1)   

      for bus in range(0, 8):
         for chip in range(0, 8):
            v = antenna.read_registers(bus, chip, antenna.LUT_ADDR, 1)[0]  
            s = 'OK' if v == int((bus << 4) + chip) else 'Error'
            print('Check bus {} chip {}, reg 0x00 = 0x{:02x}, {}'.format(bus, chip, v, s))   
  
   if args.pmic:
      status = antenna.pmic_status()
      print('Vin: {:.3f}V, Iin: {:.3f}A, Vout: {:.3f}V, Iout: {:.3f}A, Temp: {:.3f}, Pout: {:.3f}W, Status: 0x{:04x}'.format(
         status['vin'], status['iin'], status['vout'], status['iout'], status['temp'], status['pout'], status['status_word']))
      
   if args.power_on:
      antenna.power_on(True)

   if args.power_off:
      antenna.power_on(False)

   if args.enable_channel:
      channel_name = args.enable_channel[0].upper()
      enable = True if args.enable_channel[1].upper() == 'ENABLE' else False

      antenna.enable_channel(channel_name, enable)
   
   if args.set_phase:
      antenna.set_phase(args.set_phase[0], int(args.set_phase[1], 0))      

   if args.set_gain:
      antenna.set_gain(args.set_gain[0], args.set_gain[1])       

   if args.steer_beam:
      #antenna.enable_all_channel(False)

      #antenna.set_circular_polarization(args.steer_beam[0])
      #antenna.steer_beam(float(args.steer_beam[1]), args.steer_beam[2])   

      #antenna.enable_all_channel(True)
      pass

   if args.set_lp:
      arg1 = args.set_lp[0].upper()
      arg2 = args.set_lp[1].upper()
      polar = paa_control.Polar.HORI_LP if arg2 == 'H' else paa_control.Polar.VERT_LP

      calib = None
      if args.calib:
         with open(args.calib, 'r') as f:
            calib = yaml.safe_load(f)

      antenna.set_polarization(arg1, polar, calib=calib)

   if args.set_cp:
      arg1 = args.set_cp[0].upper()
      arg2 = args.set_cp[1].upper()
      polar = paa_control.Polar.LH_CP if arg2 == 'L' else paa_control.Polar.RH_CP

      calib = None
      if args.calib:
         with open(args.calib, 'r') as f:
            calib = yaml.safe_load(f)

      antenna.set_polarization(arg1, polar, calib=calib)
         
if __name__ == '__main__':
   process_command_line()