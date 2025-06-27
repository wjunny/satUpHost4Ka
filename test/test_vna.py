import sys 
sys.path.append("..") 
import matplotlib.pyplot as plt

import network_analyzer

vna = network_analyzer.NetworkAnalyzer('192.168.40.79')

vna.set_measurement('S11')
vna.set_sweep_points(201)
vna.set_frequency(30000000000, 100000000)
vna.set_average(10)
vna.set_power_level(-25)

for i in range(10):
   data = vna.retrieve_data()
   print(data)

   plt.plot(data)
   plt.show()
