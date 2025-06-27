import argparse
import mixer_conf

parser = argparse.ArgumentParser()
parser.add_argument('--device', nargs=1, metavar=('SERIAL_PORT'), required=True)
parser.add_argument('--set_lo', nargs=2, metavar=('UP|DOWN', 'FREQ(GHz)'))
parser.add_argument('--set_atten', nargs=2, metavar=('UP|DOWN', 'ATTEN(0-30db)'))
args = parser.parse_args()

mixer = mixer_conf.MixerConf(serial_port=args.device[0])

if args.set_lo:
   mixer.set_lo(args.set_lo[0].lower(), float(args.set_lo[1]))
   exit()

if args.set_atten:
   mixer.set_atten(args.set_atten[0].lower(), float(args.set_atten[1]))
   exit()
