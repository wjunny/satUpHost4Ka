import serial

class StepperMotor():
   def __init__(self, port):
      if type(port) == serial.Serial:
         self.port = port
      elif type(port) == str:
         self.port = serial.Serial(port, 115200, timeout=0.5)
      else:
         self.port = None

   def stop_motor(self):
      self.port.write([0xff, 0xf8, 0xfe])     
      self.port.read(3)

   def zero_position(self):
      self.port.write([0xff, 0xf9, 0xfe])   
      self.port.timeout = None  
      self.port.read(3)   
      self.port.timeout = 0.5    

   def rotate_motor(self, degree:float):
      dir = 0x01 if degree >= 0.0 else 0x00

      degree = abs(degree)
      steps = int(degree*180.0/360.0*400)
      steps_bytes = steps.to_bytes(4, 'big')

      self.port.write([0xff, 0xfa, dir, steps_bytes[0], steps_bytes[1], steps_bytes[2], steps_bytes[3], 0xfe]) 
      self.port.timeout = None
      self.port.read(3)
      self.port.timeout = 0.5    
    