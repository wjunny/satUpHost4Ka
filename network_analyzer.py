from keysight_ktna import *
import numpy as np
import datetime

class NetworkAnalyzer():
   def __init__(self, ip_address:str):
      self.driver = KtNA('TCPIP0::' + ip_address + '::INSTR', True, True)
      print("VNA Initialized")
      print('  identifier: ', self.driver.identity.identifier)
      print('  revision:   ', self.driver.identity.revision)
      print('  vendor:     ', self.driver.identity.vendor)
      print('  description:', self.driver.identity.description)
      print('  model:      ', self.driver.identity.instrument_model)
      print('  resource:   ', self.driver.driver_operation.io_resource_descriptor)
      print('  options:    ', self.driver.driver_operation.driver_setup)

      self.driver.classic_commands.sys_tem.fp_reset()
      self.driver.classic_commands.dis_play.win_dow.window_no = 1
      self.driver.classic_commands.dis_play.win_dow.sta_te = True

      self.average_count = 1
      
   def set_measurement(self, meas:str):
      self.driver.classic_commands.cal_culate.channel_no = 1
      self.driver.classic_commands.cal_culate.mea_sure.measurement_no = 1
      self.driver.classic_commands.cal_culate.mea_sure.de_fine(meas)
      self.driver.classic_commands.dis_play.win_dow.window_no = 1
      self.driver.classic_commands.dis_play.win_dow.tra_ce.trace_no = 1
      self.driver.classic_commands.dis_play.win_dow.tra_ce.feedmnu_mber(1)

   def set_sweep_points(self, points:int):
      self.driver.classic_commands.sen_se.sw_eep.poi_nts = points
      self.driver.classic_commands.sen_se.sw_eep.type(SweepType.LINEAR)

   def set_frequency(self, center:int, span:int):
      '''
         Units are Hz
      '''
      self.driver.classic_commands.sen_se.fre_quency.cen_ter = center
      self.driver.classic_commands.sen_se.fre_quency.span = span

   def set_average(self, count:int):
      self.average_count = count

   def retrieve_data(self) -> np.ndarray:
      self.driver.channels['Channel1'].averaging.factor = self.average_count
      self.driver.channels['Channel1'].averaging.mode = AveragingMode.SWEEP 
      self.driver.channels['Channel1'].averaging.enabled = 1
      self.driver.channels['Channel1'].averaging.restart()

      self.driver.classic_commands.sen_se.sw_eep.gr_oups_cou_nt = self.average_count
      self.driver.classic_commands.sen_se.sw_eep.mode = SweepTriggerMode.GROUPS
      self.driver.system.wait_for_operation_complete(datetime.timedelta(0, 1, 0))
      self.driver.classic_commands.cal_culate.mea_sure.measurement_no = 1
      return self.driver.classic_commands.cal_culate.mea_sure.data_query(MeasurementDataType.FORMATTED_MEAS_DATA)
   
   def set_power_level(self, level:float):
      self.driver.classic_commands.sou_rce.po_wer.le_vel = level