import os 
import time
import math
import numpy as np
from alive_progress import alive_bar
import yaml
import scipy.optimize as optimize
from enum import Enum

import paa_control
import network_analyzer
import robotic_arm
import my_utils 

OUTPUT_PATH = 'calib_output'
GRIPPER_ANGLE_HLP = 5
GRIPPER_ANGLE_VLP = 90

CALIB_STAGE = Enum('CALIB_STAGE', 'GROUP CHUNK BLOCK ARRAY')

def curve_fitting(meas_data):
   target_func = lambda p, a0, a1, a2: a0 * np.sin(p + a1) + a2

   mag_phase0 = meas_data[0][1]
   mag_phase90 = meas_data[1][1]
   mag_phase180 = meas_data[2][1]

   a2 = (mag_phase0 + mag_phase180) / 2
   a0 = np.sqrt((mag_phase0 - a2)**2 + (mag_phase90 - a2)**2)
   a1  = np.arctan2(mag_phase0 - a2, mag_phase90 - a2)
   p0 = [a0, a1, a2]

   para, _ = optimize.curve_fit(target_func, np.deg2rad(meas_data[:, 0]), meas_data[:, 1], p0=p0)
 
   phase_degree = np.linspace(0, 63, 64) * 5.625
   sine_fitting = target_func(np.deg2rad(phase_degree), *para)

   return phase_degree, sine_fitting

def calc_phase_gain_error(min_pow, max_pow, delta0, delta_emin, delta_e0):
   if min_pow < 0.0:
      min_pow = 0.0
    
   gamma = (max_pow + min_pow) / (max_pow - min_pow)
   delta = math.radians(delta0)

   case1  = lambda: (gamma / math.sqrt(1 + 2*gamma*math.cos(delta) + gamma**2), \
                     math.atan(math.sin(delta) / (math.cos(delta) + gamma)) + math.pi)
                     #delta0 - 180.0)

   case2 = lambda: (gamma / math.sqrt(1 + 2*gamma*math.cos(delta) + gamma**2), \
                     math.atan(math.sin(delta) / (math.cos(delta) + gamma)))
                     #delta0 - 180.0)
       
   case3 = lambda: (1 / math.sqrt(1 + 2*gamma*math.cos(delta) + gamma**2), \
                     math.atan(math.sin(delta) / (math.cos(delta) + 1/gamma))) 
                     #delta0 - 180.0)

   if delta_emin == '+' and (delta0 > math.pi/2 and delta0 < math.pi*2/3):
      k, x = case2()
   elif delta_emin == '+' and delta_e0 == '-': 
      k, x = case2()
   elif delta_emin == '+' and delta_e0 == '+': 
      k, x = case1()
   elif delta_emin == '-': 
      k, x = case3()
   else:    
      raise ValueError('Invalid delta_emin ({}) delta_e0 ({})'.format(delta_emin, delta_e0))
    
   return k, math.degrees(x)

def find_min_max(data, phases):
    max_idx = np.argmax(data)
    min_idx = np.argmin(data)
        
    max_pow = data[max_idx]
    min_pow = data[min_idx]

    delta0 = -phases[max_idx]

    return min_pow, max_pow, delta0

def measure_e0():
   y = float(vna.retrieve_data()[0])
                       
   return pow(10, y/10.0)

def normalize_result(calib_data:dict):
   names = list(calib_data.keys())

   k = np.array([calib_data[n]['gain'] for n in names]) 
   db = np.log10(np.min(k) / k) * 10.0

   for i, n in enumerate(names):
      calib_data[n]['gain'] = float(db[i])

   phase = np.array([calib_data[n]['phase'] for n in names])
   error = np.max(phase) - phase

   for i, n in enumerate(names):
      calib_data[n]['phase'] = float(error[i])   

def merge_result(stage:CALIB_STAGE, polar:paa_control.Polar, input:dict, output:dict):
   if stage == CALIB_STAGE.GROUP:
      for k, v in input.items():
         output[k] = v
   elif stage == CALIB_STAGE.CHUNK:
      group_channels = my_utils.GROUP_CHANNEL_H if polar == paa_control.Polar.HORI_LP else my_utils.GROUP_CHANNEL_V

      for k, v in input.items():
         phase = v['phase']
         gain = v['gain']

         for chn in group_channels[int(k[1])-1][int(k[2])-1]:
            output[chn]['phase'] += phase
            output[chn]['gain'] += gain
   elif stage == CALIB_STAGE.BLOCK: 
      group_channels = my_utils.GROUP_CHANNEL_H if polar == paa_control.Polar.HORI_LP else my_utils.GROUP_CHANNEL_V

      for k, v in input.items():
         phase = v['phase']
         gain = v['gain'] 
         
         chunk = my_utils.CHUNKS[int(k[1])-1][int(k[2])-1]
         for group in chunk:
            for chn in group_channels[group[0]-1][group[1]-1]:
               output[chn]['phase'] += phase
               output[chn]['gain'] += gain   
   elif stage == CALIB_STAGE.ARRAY:
      for k, v in input.items():
         phase = v['phase']
         gain = v['gain']

         block_channel = my_utils.BLOCK_CHANNEL_H if polar == paa_control.Polar.HORI_LP else my_utils.BLOCK_CHANNEL_V
         channels = block_channel[int(k[1])-1]
         for chn in channels:
            output[chn]['phase'] += phase
            output[chn]['gain'] += gain

def save_log(path:str, content:str):
   with open(path, 'w') as f:
      f.write(content)
      print(content)

def calibration_core(polar:paa_control.Polar, level:CALIB_STAGE=CALIB_STAGE.ARRAY) -> dict:

   def rotate_efv(element, gain_offset:float=0.0):
      phase_shifts = (90.0, 180.0, 270.0)
      length = len(phase_shifts)
      measurment = np.empty((length, 2))

      with alive_bar(length) as bar:
         for i in range(0, length):
            phase_shift = phase_shifts[i]
         
            if level == CALIB_STAGE.GROUP:
               if my_utils.is_inverting_channel(element):
                  phase_shift += 180.0
                  phase_shift = my_utils.wrap360(phase_shift)
               paa.set_phase(element, my_utils.phase_to_index(phase_shift))
               paa.load_control()
            else:
               paa.set_polarization(element, polar, calib_result, phase_offset=phase_shift, 
                                    gain_offset=gain_offset, active_channel=False) 

            y = float(vna.retrieve_data()[0])
                       
            power = pow(10, y/10.0)
            #print(y, power)
            measurment[i] = [phase_shifts[i], power]

            bar.title = element
            bar()

      return measurment        
   
   if level == CALIB_STAGE.ARRAY:
      calib_result = calibration_core(polar, level=CALIB_STAGE.BLOCK)
      calib_units = [{'unit':'ALL', 'ele':['B1', 'B2', 'B3', 'B4']}]
   elif level == CALIB_STAGE.BLOCK:
      calib_result = calibration_core(polar, level=CALIB_STAGE.CHUNK)
      calib_units = [{'unit':'B1', 'ele':['C11', 'C12', 'C21', 'C22']}, {'unit':'B2', 'ele':['C13', 'C14', 'C23', 'C24']},
                     {'unit':'B3', 'ele':['C31', 'C32', 'C41', 'C42']}, {'unit':'B4', 'ele':['C33', 'C34', 'C43', 'C44']}]
   elif level == CALIB_STAGE.CHUNK:
      calib_result = calibration_core(polar, level=CALIB_STAGE.GROUP)
      calib_units = [{'unit':'C{}{}'.format(i+1, j+1), 'ele':['G{}{}'.format(g[0], g[1]) for g in my_utils.CHUNKS[i][j]]} for i in range(0, 4) for j in range(0, 4)]   
   elif level == CALIB_STAGE.GROUP:
      group_channel = my_utils.GROUP_CHANNEL_H if polar == paa_control.Polar.HORI_LP else my_utils.GROUP_CHANNEL_V
      calib_units = [{'unit':'G{}{}'.format(i+1, j+1), 'ele':group_channel[i][j]} for i in range(0, 8) for j in range(0, 8)]
      calib_result = {}

   print('\nStage: {}\n'.format(level.name))

   for unit in calib_units:
      temp_result = {}

      paa.set_polarization(unit['unit'], polar, calib_result)
      e0 = measure_e0()   

      for ele in unit['ele']:
         paa.set_polarization(unit['unit'], polar, calib_result, active_channel=False)

         measurment = rotate_efv(ele)
         four_points = np.concatenate((np.array([[0.0, e0]]), measurment), axis=0)

         polar_str = '_h' if polar == paa_control.Polar.HORI_LP else '_v'
         np.savetxt(OUTPUT_PATH + '/log/' + unit['unit'] + '_' + ele + polar_str +'_refv.log', four_points, fmt='%.10f')

         phase_degree, fitting_data = curve_fitting(four_points)
         min_pow, max_pow, delta0 = find_min_max(fitting_data, phase_degree)
         emin = min_pow

         #print('min_pow: {:.3f}, max_pow: {:.3f}, delta0: {:.3f}'.format(min_pow, max_pow, delta0))

         paa.set_polarization(unit['unit'], polar, calib_result, gain_offset=-5.0, active_channel=False)
         e0_2 =  measure_e0()

         measurment = rotate_efv(ele, -5.0)

         four_points = np.concatenate((np.array([[0.0, e0_2]]), measurment), axis=0)
         phase_degree, fitting_data = curve_fitting(four_points)
         emin_2, _, _ = find_min_max(fitting_data, phase_degree)

         delta_e0 = '-' if e0_2 - e0 < 0.0 else '+'
         delta_emin = '-' if emin_2 - emin < 0.0 else '+'

         print('e0: {:.8f}, emin: {:.8f}, e0_2: {:.8f}, emin_2: {:.8f}, delta_emin: {}, delta_e0: {}'.
            format(e0, emin, e0_2, emin_2, delta_emin, delta_e0))
         
         gain_error, phase_error = calc_phase_gain_error(min_pow, max_pow, delta0, delta_emin, delta_e0)
         #print('phase: {:.6f}, gain: {:.6f}\n'.format(phase_error, gain_error))
       
         temp_result[ele] = {'gain':float(gain_error), 'phase':float(phase_error)}

         save_log(OUTPUT_PATH + '/log/' + unit['unit'] + '_' + ele + polar_str + '_cal.log', 
            'min_pow: {:.8f}, max_pow: {:.8f}, delta0: {:.8f} '
            'e0: {:.8f}, emin: {:.8f}, e0_2: {:.8f}, emin_2: {:.8f}, delta_emin: {}, delta_e0: {} '
            'phase: {:.8f}, gain: {:.8f}\n'.
               format(min_pow, max_pow, delta0, e0, emin, e0_2, emin_2, 
                     delta_emin, delta_e0, phase_error, gain_error))
   
      normalize_result(temp_result)
      merge_result(level, polar, temp_result, calib_result)  

   return calib_result   
   
def run_calibration(settings:dict):
   global paa
   paa = paa_control.PAAControl(settings['paa_serial_port'], settings['paa_type'], 8)
   paa.enable_amplifier(False)
   paa.initialize_antenna() 
   
   global vna
   vna = network_analyzer.NetworkAnalyzer(settings['vna_ip_address'])
   vna.set_measurement('S21')   
   vna.set_frequency(settings['vna_center_freq']*1e6, 0)
   vna.set_sweep_points(1)
   vna.set_average(settings['vna_average_count'])
   vna.set_power_level(settings['vna_power_level'])

   global arm
   arm = robotic_arm.RoboticArmControl(settings['robotic_arm_serial_port'])
   arm.rotate_gripper(GRIPPER_ANGLE_HLP)   
   time.sleep(2)

   paa.enable_amplifier(True)

   calib = calibration_core(paa_control.Polar.HORI_LP)
   print('\n')
   arm.rotate_gripper(GRIPPER_ANGLE_VLP)   
   time.sleep(2)
   calib |= calibration_core(paa_control.Polar.VERT_LP)

   paa.enable_amplifier(False)

   with open(OUTPUT_PATH + '/calibration-' + my_utils.timestamp() + '.yaml', 'w') as file:
      yaml.dump(calib, file)

if __name__ == '__main__':
   if not os.path.exists(OUTPUT_PATH):
      os.mkdir(OUTPUT_PATH)
   if not os.path.exists(OUTPUT_PATH + '/log'):
      os.mkdir(OUTPUT_PATH +'/log')

   with open('calib_settings.yaml', 'r') as f:
      settings = yaml.safe_load(f)

   run_calibration(settings)
