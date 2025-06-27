import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
import scipy.optimize as optimize
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', type=str)
args = parser.parse_args()
if not args.file:
    exit()

data_array = np.loadtxt(args.file)

mag_phase0 = data_array[0][1]
mag_phase90 = data_array[1][1]
mag_phase180 = data_array[2][1]
mag_phase270 = data_array[3][1]

def target_func(p, a0, a1, a2):
    return a0 * np.sin(p + a1) + a2

a2 = (mag_phase0 + mag_phase180) / 2
a0 = np.sqrt((mag_phase0 - a2)**2 + (mag_phase90 - a2)**2)
a1  = np.arctan2(mag_phase0 - a2, mag_phase90 - a2)
p0 = [a0, a1, a2]

para, _ = optimize.curve_fit(target_func, np.deg2rad(data_array[:, 0]), data_array[:, 1], p0=p0)

phase_degree = np.linspace(0, 63, 64) * 5.625
sine_fitting = target_func(np.deg2rad(phase_degree), *para)

max_idx = np.argmax(sine_fitting)
min_idx = np.argmin(sine_fitting)
max_pow = sine_fitting[max_idx]
min_pow = sine_fitting[min_idx]

fig, ax = plt.subplots()

trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                       x=0.05, y=0.10, units='inches')

ax.plot(phase_degree, sine_fitting, label='Fit curve', color='blue')
ax.plot(0, mag_phase0, '.', markersize=10, color='magenta')
ax.plot(90, mag_phase90, '.', markersize=10, color='magenta')
ax.plot(180, mag_phase180, '.', markersize=10, color='magenta')
ax.plot(270, mag_phase270, '.', markersize=10, color='magenta')

max_phase = max_idx * 5.625
ax.plot(max_phase, max_pow, 'v:r', markersize=7)
data_str = '{:.3f}  {:.3f}'.format(max_phase, max_pow)
ax.text(max_phase, max_pow, data_str, color='red', transform=trans_offset)

min_phase = min_idx * 5.625
ax.plot(min_phase, min_pow, '^:g', markersize=7)
data_str = '{:.3f}  {:.3f}'.format(min_phase, min_pow)
ax.text(min_phase, min_pow, data_str, color='green', transform=trans_offset)

ax.set_xlabel('Phase (Deg)')
ax.set_ylabel('Power (mW)')
plt.show()

