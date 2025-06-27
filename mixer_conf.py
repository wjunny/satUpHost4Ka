import serial
import time

class MixerConf():
    def __init__(self, **kwargs):
        if 'serial_port' in kwargs:
            self.serial_port = serial.Serial(kwargs['serial_port'], 115200, timeout=1)
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

            if 'down_lo' in kwargs:
                self.set_lo('down', kwargs['down_lo']) 
            if 'down_atten' in kwargs:
                self.set_atten('down', kwargs['down_atten']) 
            if 'up_lo' in kwargs:
                self.set_lo('up', kwargs['up_lo']) 
            if 'up_atten' in kwargs:
                self.set_atten('up', kwargs['up_atten'])       

    def crc16(self, data : bytearray, offset , length):
        if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
            return 0
   
        crc = 0xFFFF

        for i in range(0, length):
            crc ^= data[offset + i] << 8
            for j in range(0, 8):
                if (crc & 0x8000) > 0:
                    crc =(crc << 1) ^ 0x1021
                else:
                    crc = crc << 1

        return crc & 0xFFFF

    def set_lo(self, type:str, freq:float):
        cmd_buffer = [0xaa, 0x55, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] 

        if type == 'down':
            cmd_buffer[4] = 0x0e
        elif type == 'up':
            cmd_buffer[4] = 0x12   
        else:
            return   

        lo_value = int(freq*1000).to_bytes(2, 'big')
        cmd_buffer[8:10] = lo_value
        checksum = self.crc16(cmd_buffer, 0, 10).to_bytes(2, 'big')
        cmd_buffer[10:12] = checksum

        self.serial_port.write(cmd_buffer)
        response = self.serial_port.read(12)

        if self.check_response(response):
            print('Mixer: LO frequency is set successfully.')
        else:
            print('Mixer: An error occurred.')    

    def set_atten(self, type:str, db:float):
        if db > 30.0:
            return

        cmd_buffer = [0xaa, 0x55, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] 

        if type == 'down':
            cmd_buffer[4] = 0x15
        elif type == 'up':
            cmd_buffer[4] = 0x14   
        else:
            return   

        db_value = int(db*10).to_bytes(2, 'big')
        cmd_buffer[8:10] = db_value
        checksum = self.crc16(cmd_buffer, 0, 10).to_bytes(2, 'big')
        cmd_buffer[10:12] = checksum

        self.serial_port.write(cmd_buffer)
        response = self.serial_port.read(12)
       
        if self.check_response(response):
            print('Mixer: Attenuation is set successfully.')
        else:
            print('Mixer: An error occurred.')    

    def check_response(self, buff):
        if len(buff) != 12:
            return False
        
        checksum = self.crc16(buff, 0, 10)
        if int.from_bytes(buff[10:12], 'big') == checksum:
            return True

        return False    

