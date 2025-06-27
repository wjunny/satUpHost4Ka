import argparse
import stepper_motor

parser = argparse.ArgumentParser()
parser.add_argument('--device', nargs=1, metavar=('SERIAL_PORT'), required=True)
parser.add_argument('--zero', action='store_true')
parser.add_argument('--stop', action='store_true')
parser.add_argument('--rotate', nargs=1, metavar=('DEG'))

args = parser.parse_args()

motor = stepper_motor.StepperMotor(args.device[0])

if args.zero:
    motor.zero_position()

if args.stop:
    motor.stop_motor()

if args.rotate:
    motor.rotate_motor(float(args.rotate[0]))
