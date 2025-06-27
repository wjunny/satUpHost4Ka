import serial
import time

def calc_crc(buf):
   crc = 0xFFFF

   for d in buf:
      crc = (crc ^ d) & 0xffff

      for _ in range(8):
         if crc & 0x0001:
            crc >>= 1
            crc = (crc ^ 0xA001) & 0xffff
         else:
            crc >>= 1
            crc &= 0xffff

   return crc

serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
serial_port.reset_input_buffer()
serial_port.reset_output_buffer()   

register = [0x000201]
payload_length = len(register)*3 + 4
frame_length = payload_length + 6

#write register test
cmd = [int(0)]*frame_length
cmd[0] = 0xff
cmd[1] = 0x08
cmd[2] = 0x02
cmd[3] = payload_length
cmd[4] = 0x00
cmd[5] = 0x00
cmd[6] = 0x4d
cmd[7] = len(register)

data_bytes  = []
for reg in register: 
   data_bytes += reg.to_bytes(3, 'big')
cmd[8:-2] = data_bytes

crc16 = calc_crc(cmd[1:-2])
cmd[-2:] = crc16.to_bytes(2, 'big')

print('wrtie: {}'.format([hex(x) for x in cmd]))
serial_port.write(cmd)

resp = serial_port.read(256)
print('recv: {}, length: {}'.format([hex(x) for x in resp], len(resp)))

#read register test
cmd = [int(0)]*10
cmd[0] = 0xff
cmd[1] = 0x08
cmd[2] = 0x01
cmd[3] = 4
cmd[4] = 0x00
cmd[5] = 0x00
cmd[6] = 0x52
cmd[7] = 0x01
crc16 = calc_crc(cmd[1:-2])
cmd[-2:] = crc16.to_bytes(2, 'big')

print('wrtie: {}'.format([hex(x) for x in cmd]))
serial_port.write(cmd)

resp = serial_port.read(256)
print('recv: {}, length: {}'.format([hex(x) for x in resp], len(resp)))

'''
#rfen test
cmd = [int(0)]*7
cmd[0] = 0xff
cmd[1] = 0x08
cmd[2] = 0x03
cmd[3] = 1
cmd[4] = 0xff
crc16 = calc_crc(cmd[1:-2])
cmd[-2:] = crc16.to_bytes(2, 'big')

print('wrtie: {}'.format([hex(x) for x in cmd]))
serial_port.write(cmd)

resp = serial_port.read(256)
print('recv: {}, length: {}'.format([hex(x) for x in resp], len(resp)))

time.sleep(2)

cmd = [int(0)]*7
cmd[0] = 0xff
cmd[1] = 0x08
cmd[2] = 0x03
cmd[3] = 1
cmd[4] = 0x00
crc16 = calc_crc(cmd[1:-2])
cmd[-2:] = crc16.to_bytes(2, 'big')

print('wrtie: {}'.format([hex(x) for x in cmd]))
serial_port.write(cmd)

resp = serial_port.read(256)
print('recv: {}, length: {}'.format([hex(x) for x in resp], len(resp)))
'''

'''
#load test
time.sleep(2)

cmd = [int(0)]*6
cmd[0] = 0xff
cmd[1] = 0x08
cmd[2] = 0x04
cmd[3] = 0
crc16 = calc_crc(cmd[1:-2])
cmd[-2:] = crc16.to_bytes(2, 'big')

print('wrtie: {}'.format([hex(x) for x in cmd]))
serial_port.write(cmd)

resp = serial_port.read(256)
print('recv: {}, length: {}'.format([hex(x) for x in resp], len(resp)))
'''

'''
#pmic status test
cmd = [int(0)]*6
cmd[0] = 0xff
cmd[1] = 0x08
cmd[2] = 0x05
cmd[3] = 0
crc16 = calc_crc(cmd[1:-2])
cmd[-2:] = crc16.to_bytes(2, 'big')

print('wrtie: {}'.format([hex(x) for x in cmd]))
serial_port.write(cmd)

resp = serial_port.read(256)
print('recv: {}, length: {}'.format([hex(x) for x in resp], len(resp)))

vin_raw = int.from_bytes(resp[4:6], byteorder='big', signed=False)
iin_raw = int.from_bytes(resp[6:8], byteorder='big', signed=False)
vout_raw = int.from_bytes(resp[8:10], byteorder='big', signed=False)
iout_raw = int.from_bytes(resp[10:12], byteorder='big', signed=False)
temp_raw = int.from_bytes(resp[12:14], byteorder='big', signed=False)
pout_raw = int.from_bytes(resp[14:16], byteorder='big', signed=False)
status_word = int.from_bytes(resp[16:18], byteorder='big', signed=False)
   
print('Vin: {:.3f}V, Iin: {:.3f}A, Vout: {:.3f}V, Iout: {:.3f}A, Temp: {:.3f}, Pout: {:.3f}W, Status: 0x{:04x}'.format(
   float(vin_raw&0x7ff)*0.25, float(iin_raw&0x7ff)*0.25, float(vout_raw&0xfff)*0.001, 
   float(iout_raw&0x7ff), float(temp_raw&0xff), float(pout_raw&0x7ff), status_word))
'''