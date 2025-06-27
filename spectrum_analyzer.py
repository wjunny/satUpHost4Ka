import pyvisa

class SpectrumAnalyzerControl():
   def __init__(self, ip_address:str, port:str):
      self.resource_manager = pyvisa.ResourceManager()

      resource_name = 'TCPIP0::' + ip_address + '::' + port + '::SOCKET'
      self.resource = self.resource_manager.open_resource(resource_name)
      self.resource.read_termination = '\n'
      self.resource.write_termination = '\n'
      self.resource.timeout = 5000.0

      self.resource.write('*CLS')
      self.resource.write('*RST')
      self.resource.write(':UNIT:POWer DBM')

   def query_id(self):
      return self.resource.query('*IDN?')
   
   def set_center_freq(self, freq):
      '''freq: Mhz'''

      freq_str = str(int(freq))
      cmd = ':SENSe:FREQuency:CENTer ' + freq_str + 'MHz'
      self.resource.write(cmd)

   def set_span(self, freq):
      '''freq: Mhz'''

      freq_str = str(int(freq))
      cmd = ':SENSe:FREQuency:SPAN ' + freq_str + 'MHz'
      self.resource.write(cmd)

   def set_start_freq(self, freq):
      '''freq: Mhz'''

      freq_str = str(int(freq))
      cmd = ':SENSe:FREQuency:START ' + freq_str + 'MHz'
      self.resource.write(cmd)

   def set_stop_freq(self, freq):
      '''freq: Mhz'''

      freq_str = str(int(freq))
      cmd = ':SENSe:FREQuency:STOP ' + freq_str + 'MHz'
      self.resource.write(cmd)

   def single_sweep(self, onoff):
      cmd = ':INITiate:CONTinuous '
      if onoff:
         cmd += 'OFF'
      else:   
         cmd += 'ON'

      self.resource.write(cmd)   

   def trigger_sweep(self):
      self.resource.write(':INITiate:IMMediate')

      complete = 0
      while complete == 0:
         complete = self.resource.query('*OPC?')

   def average_count(self, count):
      cmd = ':SENSe:AVERage:COUNt ' + str(count)
      self.resource.write(cmd)  

   def enable_average(self, enable):
      cmd = ':SENSe:AVERage '
      if enable:
         cmd += 'ON'
      else :
         cmd += 'OFF'

      self.resource.write(cmd)  

   def peak(self):
      self.resource.write(':CALCulate:MARKer:MAXimum')

      x = self.resource.query_ascii_values(':CALCulate:MARKer:X?')
      y = self.resource.query_ascii_values(':CALCulate:MARKer:Y?')

      return x[0], y[0]

   def trace_data(self, trace_name):
      return self.resource.query_ascii_values(':TRAC:DATA? ' + trace_name)
