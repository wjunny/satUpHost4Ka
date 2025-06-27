import serial

class RoboticArmControl():
   initial_pos = {1:int(2500), 2:int(1500), 3:int(1500), 4:int(1500), 5:int(1500), 6:int(1500)}
   final_pos = {3:int(720), 4:int(500), 5:int(500)}

   def __init__(self, serial_device):
      try:
         self.serial_port = serial.Serial(serial_device, 9600, timeout=0.5)
         self.serial_port.reset_input_buffer()
         self.serial_port.reset_output_buffer()   
      except serial.serialutil.SerialException as e:  
         print(e)
         self.serial_port = None

   def control_command(self, pos, action_time):
      pos_len = len(pos) 
      if pos_len > 6 or pos_len == 0:
         return None
      
      cmd_len = pos_len*3 + 5
      cmd = [int(0)] * (cmd_len + 2)
      cmd[0] = 0x55
      cmd[1] = 0x55
      cmd[2] = int(cmd_len)
      cmd[3] = 0x03
      cmd[4] = int(pos_len)
      cmd[5] = int(int(action_time)%256)
      cmd[6] = int(int(action_time)/256)
      
      param = []
      for k, v in pos.items():
         param += [int(k), int(int(v)%256), int(int(v)/256)]
      cmd[7:] = param
      
      return cmd

   def reset_robot_arm(self):
      self.serial_port.write(self.control_command(self.initial_pos, 2000))

   def set_robot_arm_position(self):
      self.serial_port.write(self.control_command(self.final_pos, 2000))
      pos = {2:2000 * int(3) / 180.0 + 500.0}
      self.serial_port.write(self.control_command(pos, 2000))

   def open_gripper(self, is_open):
      pos = {1:500} if is_open else {1:2500}
      self.serial_port.write(self.control_command(pos, 100))

   def rotate_gripper(self, degree):
      if degree < 0 or degree > 180:
         return
    
      pos = {2:2000 * int(degree) / 180.0 + 500.0}
      self.serial_port.write(self.control_command(pos, 100))
