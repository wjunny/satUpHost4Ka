import cProfile
import pstats
from pstats import SortKey
import paa_control
import my_utils
import time
import random

paa = paa_control.PAAControl('/dev/ttyUSB1', 'Receiving', 8)

#test_data = {}
#for bus_num in range(0, 8):
#   test_data[bus_num] = [[random.randint(0, 0xffffff) for j in range(6)] for i in range(8)]

#cProfile.run('paa.write_register_burst(0x00, test_data)')

cProfile.run('paa.steer_beam(20)')
