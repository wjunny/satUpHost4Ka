import argparse
import robotic_arm

def process_command_line():
   parser = argparse.ArgumentParser()
   parser.add_argument('--device', nargs=1, metavar=('SERIAL_PORT'), required=True)
   parser.add_argument('--reset', action='store_true')
   parser.add_argument('--set', action='store_true')
   parser.add_argument('--open_gripper', nargs=1, choices=('open', 'close'))
   parser.add_argument('--rotate_gripper', nargs=1, metavar=('DEG'))

   args = parser.parse_args()

   arm = robotic_arm.RoboticArmControl(args.device[0])

   if args.reset:
      arm.reset_robot_arm()
      print('Arm reset completed')

   if args.set:
      arm.set_robot_arm_position()
      print('Operation completed')  
      
   if args.open_gripper:   
      is_open = True if args.open_gripper[0] == 'open' else False
      arm.open_gripper(is_open)
      print('Operation completed')         

   if args.rotate_gripper:   
      degree = int(args.rotate_gripper[0])
      arm.rotate_gripper(degree)   
      print('Operation completed')         
   
if __name__ == '__main__':
   process_command_line()
