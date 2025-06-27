import os
import sys
import serial
import serial.tools.list_ports
import yaml
import math
import debugpy
from datetime import *
import numpy as np
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Slot

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

from ui_form import Ui_MainWindow

import network_analyzer
import paa_control
import stepper_motor
import robotic_arm
import my_utils

SETTINGS_FILE = 'settings.yaml'

class MplCanvas(FigureCanvasQTAgg):
   def __init__(self, parent=None, width=5, height=4, dpi=110):
      self.fig = Figure(figsize=(width, height), dpi=dpi)
      self.axes = self.fig.add_subplot(111, projection="polar")
      super(MplCanvas, self).__init__(self.fig)

class ResetMotorThread(QThread):
   def __init__(self, motor:stepper_motor.StepperMotor):
      super(ResetMotorThread, self).__init__()
      self.motor = motor

   def run(self):
      self.motor.zero_position()

class ResetRoboticArmThread(QThread):
   def __init__(self, arm:robotic_arm.RoboticArmControl):
      super(ResetRoboticArmThread, self).__init__()
      self.arm = arm

   def run(self):
      self.arm.reset_robot_arm()
      QThread.sleep(3)
      self.arm.set_robot_arm_position()
      QThread.sleep(3)
      self.arm.rotate_gripper(4)   
      #self.arm.rotate_gripper(90)  
      QThread.sleep(2)

class MeasurmentThread(QThread):
   pattern_data = Signal(list)
   error_message = Signal(str)
   save_figure = Signal(str)
   set_figure_title = Signal(str)

   def __init__(self, settings):
      super(MeasurmentThread, self).__init__()
      self.settings = settings

   def reset_actuator(self, *args):
      reset_threads = []
      for actu in args:
         if type(actu) == robotic_arm.RoboticArmControl:
            reset_threads.append(ResetRoboticArmThread(actu))
         elif type(actu) == stepper_motor.StepperMotor:
            reset_threads.append(ResetMotorThread(actu))  

      for t in reset_threads:
         t.start()

      for t in reset_threads:
         t.wait()   

   def run(self):
      paa_controller = paa_control.PAAControl(self.settings['paa_serial_port'], self.settings['paa_type'], 8)
      paa_controller.initialize_antenna()

      calib = None
      if self.settings['use_calib']:
         with open(self.settings['calib_file'], 'r') as f:
            calib = yaml.safe_load(f)
      paa_controller.set_polarization('ALL', 
            paa_control.Polar.LH_CP if self.settings['polarization'][0] == 'Left' else paa_control.Polar.RH_CP, calib=calib)
      paa_controller.steer_beam(azi_angle=self.settings['beam_az'], ele_angle=self.settings['beam_el'])

      vna = network_analyzer.NetworkAnalyzer(self.settings['vna_ip_address'])
      vna.set_measurement('S21')   
      vna.set_frequency(self.settings['vna_center_freq']*1e6, 0)
      vna.set_sweep_points(1)
      vna.set_average(self.settings['vna_average_count'])
      vna.set_power_level(self.settings['vna_power_level'])

      motor = stepper_motor.StepperMotor(self.settings['motor_serial_port'])
      arm = robotic_arm.RoboticArmControl(self.settings['robotic_arm_serial_port'])
      self.reset_actuator(motor, arm)

      def meas_loop():
         for i in np.arange(-90.0, 90.1, step):
            if QThread.currentThread().isInterruptionRequested():
               return False
                 
            theta.append(math.radians(float(i)))
         
            value = vna.retrieve_data()
            value = float(value[0])
      
            '''if value <= -30.0:
               value = -29.0'''

            if value <= -25:
               POLAR_COORD_MAX = -15
               POLAR_COORD_MIN = -65
            else:
               POLAR_COORD_MAX = value+10
               POLAR_COORD_MIN = POLAR_COORD_MAX -50

            measurment.append(value)

            self.pattern_data.emit([theta, measurment])   

            motor.rotate_motor(step)
            #QThread.msleep(500)

         return True   
           
      step = float(self.settings['motor_step'])
      theta = []
      measurment = []

      paa_controller.enable_amplifier(True)

      self.set_figure_title.emit('Radiation Pattern (Horizontal)')

      if not meas_loop():
         paa_controller.enable_amplifier(False)
         return

      fn = my_utils.timestamp() + '_rp_hori'
      self.save_figure.emit(fn)

      arm.rotate_gripper(90)
      self.reset_actuator(motor)

      self.set_figure_title.emit('Radiation Pattern (Vertical)')
      theta = []
      measurment = []

      if not meas_loop():
         paa_controller.enable_amplifier(False)
         return

      fn = my_utils.timestamp() + '_rp_vert'
      self.save_figure.emit(fn)

      paa_controller.enable_amplifier(False)

      print('Measurment Finished.')   
         
class AnalyzerMainWindow(QMainWindow, Ui_MainWindow):
   '''POLAR_COORD_MAX = 20'''
   '''POLAR_COORD_MIN = -30'''

   POLAR_COORD_MAX = -15
   POLAR_COORD_MIN = -65

   def __init__(self, *args, obj=None, **kwargs):
      super(AnalyzerMainWindow, self).__init__(*args, **kwargs)
  
      self.saved_settings = self.load_saved_settings()
      if self.saved_settings is not None and len(self.saved_settings) != 0:
         self.setup_ui(self.saved_settings)
      else:
         self.saved_settings = dict()
         self.setup_ui()

      self.meas_thread = MeasurmentThread(self.saved_settings)
      self.meas_thread.pattern_data.connect(self.receive_pattern_data)
      self.meas_thread.finished.connect(self.thread_finished)
      self.meas_thread.error_message.connect(self.meas_thread_error_message)
      self.meas_thread.save_figure.connect(self.save_figure)
      self.meas_thread.set_figure_title.connect(self.set_figure_title)

      self.StartButton.clicked.connect(self.start_button_clicked)
      self.StopButton.setEnabled(False)
      self.StopButton.clicked.connect(self.stop_button_clicked)
      self.UseCalibCheckBox.clicked.connect(self.checkbox_clicked)
      self.OpenCalibFileButton.clicked.connect(self.open_calib_file)

      self.VNAIPEdit.textEdited.connect(self.text_edited)
      self.CenterFreqEdit.textEdited.connect(self.text_edited)
      self.AverageCountEdit.textEdited.connect(self.text_edited)
      self.PowerLevelEdit.textEdited.connect(self.text_edited)
      self.AzEdit.textEdited.connect(self.text_edited)
      self.EleEdit.textEdited.connect(self.text_edited)
      self.CompEdit.textEdited.connect(self.text_edited)

      self.PAAPortComboBox.currentIndexChanged.connect(self.index_changed)
      self.AntTypeComboBox.currentIndexChanged.connect(self.index_changed)
      self.ArmPortComboBox.currentIndexChanged.connect(self.index_changed)
      self.MotorPortComboBox.currentIndexChanged.connect(self.index_changed)
      self.MotorStepComboBox.currentIndexChanged.connect(self.index_changed)
      self.PolarComboBox.currentIndexChanged.connect(self.index_changed)

      self.settings_table = {
         self.VNAIPEdit: ['vna_ip_address', str],
         self.CenterFreqEdit: ['vna_center_freq', int],
         self.AverageCountEdit: ['vna_average_count', int],
         self.PowerLevelEdit: ['vna_power_level', float],
         self.AzEdit: ['beam_az', int],
         self.EleEdit: ['beam_el', int],
         self.CompEdit: ['gain_comp', float],
         self.PAAPortComboBox: ['paa_serial_port', str],
         self.AntTypeComboBox: ['paa_type', str],
         self.ArmPortComboBox: ['robotic_arm_serial_port', str],
         self.MotorStepComboBox: ['motor_step', str],
         self.MotorPortComboBox: ['motor_serial_port', str],
         self.PolarComboBox: ['polarization', str],
      }

   def error_message(self, msg):
      QMessageBox.critical(self, 'Error', msg, buttons=QMessageBox.Ok)

   def load_saved_settings(self):
      try:
         with open(SETTINGS_FILE, 'r') as stream:
            dict = yaml.safe_load(stream)
      except OSError as e:
         print(str(e))
         return None
      except yaml.YAMLError as e:   
         print(str(e))
         stream.close()
         return None

      stream.close()
      return dict   
   
   def check_settings(self):
      try:
         if self.saved_settings['paa_serial_port'] == '':
            raise ValueError('Incorrect PAA serial port settings')
         
         if self.saved_settings['paa_type'] != 'Receiving' and self.saved_settings['paa_type'] != 'Transmitting':
            raise ValueError('Incorrect PAA type settings') 
         
         if self.saved_settings['robotic_arm_serial_port'] == '':
            raise ValueError('Incorrect Robotic Arm serial port settings') 
         
         if self.saved_settings['motor_serial_port'] == '':
            raise ValueError('Incorrect Motor serial port settings')
         
         if self.saved_settings['motor_step'] == '':
            raise ValueError('Incorrect Motor Step settings') 
         
         if self.saved_settings['vna_ip_address'] == '':
            raise ValueError('Incorrect SA IP Address settings') 

         if self.saved_settings['polarization'] == '':
            raise ValueError('Incorrect Polarization settings') 

         _ = self.saved_settings['vna_center_freq']
         _ = self.saved_settings['vna_average_count']
         _ = self.saved_settings['vna_power_level']
         _ = self.saved_settings['beam_az']
         _ = self.saved_settings['beam_el']
         _ = self.saved_settings['gain_comp']
      except ValueError as e:
         self.error_message(repr(e))
         return False
      except KeyError as e:
         msg = 'Parameter ' + str(e) + ' is not available .'
         self.error_message(msg)
         return False

      return True   
   
   def setup_ui(self, param=None):
      super().setupUi(self)      

      ports_info = serial.tools.list_ports.comports()
      for port, desc, hwid in sorted(ports_info):
         self.PAAPortComboBox.addItem(port)
         self.ArmPortComboBox.addItem(port)
         self.MotorPortComboBox.addItem(port)

      self.PAAPortComboBox.setCurrentIndex(-1)
      self.ArmPortComboBox.setCurrentIndex(-1)
      self.PolarComboBox.setCurrentIndex(-1)
      self.MotorStepComboBox.setCurrentIndex(-1)
      self.AntTypeComboBox.setCurrentIndex(-1)
      self.MotorPortComboBox.setCurrentIndex(-1)

      ip_regex = QRegExp('((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])')
      ip_validator = QRegExpValidator(ip_regex)
      self.VNAIPEdit.setValidator(ip_validator)
     
      freq_regex = QRegExp('^([0-9]|[1-9][0-9]|[1-9][0-9]{2}|[1-9][0-9]{3}|[1-5][0-9]{4}|3[0-9][0-9]{3}|39[0-9][0-9]{2}|399[0-9][0-9]|40000)$')
      freq_validator = QRegExpValidator(freq_regex)
      self.CenterFreqEdit.setValidator(freq_validator)

      average_regex = QRegExp('^[1-9][0-9]{0,2}$')
      average_validator = QRegExpValidator(average_regex)
      self.AverageCountEdit.setValidator(average_validator)

      power_regex = QRegExp('^(-?[0-9][0-9]\\.[0-9][0-9]|[0-9]\\.[0-9][0-9])$')
      power_validator = QRegExpValidator(power_regex)
      self.PowerLevelEdit.setValidator(power_validator)
          
      degree_regex = QRegExp('^(-?[1-9]|-?[1-8]?[0-9]?|90|-90)$')
      degree_validator = QRegExpValidator(degree_regex)
      self.AzEdit.setValidator(degree_validator)
      self.AzEdit.setCursorPosition(0)
      
      self.EleEdit.setValidator(degree_validator)
      self.EleEdit.setCursorPosition(0)
      
      regex = QRegExp('^([0-9][0-9]\\.[0-9][0-9]|[0-9]\\.[0-9][0-9])$')
      validator = QRegExpValidator(regex)
      self.CompEdit.setValidator(validator)
      self.CompEdit.setCursorPosition(0)
          
      self.UseCalibCheckBox.setCheckState(Qt.Unchecked)
      self.CalibFileLineEdit.setEnabled(False)
      self.OpenCalibFileButton.setEnabled(False)

      if param is not None:
         if 'paa_serial_port' in self.saved_settings:
            self.PAAPortComboBox.setCurrentIndex(self.PAAPortComboBox.findText(param['paa_serial_port']))

         if 'motor_serial_port' in self.saved_settings:
            self.MotorPortComboBox.setCurrentIndex(self.PAAPortComboBox.findText(param['motor_serial_port']))   

         if 'robotic_arm_serial_port' in self.saved_settings:  
            self.ArmPortComboBox.setCurrentIndex(self.ArmPortComboBox.findText(param['robotic_arm_serial_port']))
            
         if 'paa_type' in self.saved_settings:
            self.AntTypeComboBox.setCurrentIndex(self.AntTypeComboBox.findText(param['paa_type']))  

         if 'motor_step' in self.saved_settings:  
            self.MotorStepComboBox.setCurrentIndex(self.MotorStepComboBox.findText(param['motor_step']))   

         if 'polarization' in self.saved_settings:   
            self.PolarComboBox.setCurrentIndex(self.PolarComboBox.findText(param['polarization']))

         if 'vna_ip_address' in self.saved_settings:
            self.VNAIPEdit.setText(param['vna_ip_address'])

         if 'vna_center_freq' in self.saved_settings:
            self.CenterFreqEdit.setText(str(param['vna_center_freq']))

         if 'vna_average_count' in self.saved_settings:  
            self.AverageCountEdit.setText(str(param['vna_average_count']))

         if 'vna_power_level' in self.saved_settings:
            self.PowerLevelEdit.setText(str(param['vna_power_level']))   

         if 'beam_az' in self.saved_settings:   
            self.AzEdit.setText(str(param['beam_az']))
         if 'beam_el' in self.saved_settings:   
            self.EleEdit.setText(str(param['beam_el']))
         if 'gain_comp' in self.saved_settings:   
            self.CompEdit.setText(str(param['gain_comp']))

         if 'use_calib' in self.saved_settings: 
            self.UseCalibCheckBox.setCheckState(Qt.Checked if param['use_calib'] else Qt.Unchecked)
            if self.UseCalibCheckBox.isChecked():
               self.CalibFileLineEdit.setEnabled(True)
               self.OpenCalibFileButton.setEnabled(True)
            else:
               self.CalibFileLineEdit.setEnabled(False)
               self.OpenCalibFileButton.setEnabled(False)

         if 'calib_file' in self.saved_settings:
            self.CalibFileLineEdit.setText(param['calib_file'])
    
      self.canvas = MplCanvas()
      self.line2d = self.canvas.axes.plot([], [])[0]
      self.canvas.axes.set_ylim(ymin=self.POLAR_COORD_MIN, ymax=self.POLAR_COORD_MAX)
      self.canvas.axes.grid(True)
      self.canvas.axes.set_theta_zero_location('N')
      self.canvas.axes.set_thetalim(thetamin=-180.0, thetamax=180.0)
      self.canvas.axes.set_thetagrids(np.arange(-180.0, 180.0, 10.0))
      self.canvas.axes.set_theta_direction(-1)
      self.canvas.axes.set_rlabel_position(-65.0)
      self.canvas.axes.set_title('', va='bottom')
      self.horizontalLayout_3.addWidget(self.canvas)

      self.anim = animation.FuncAnimation(self.canvas.fig, self.animate, interval=20, blit=True, cache_frame_data=False)

   def closeEvent(self, event):
      with open(SETTINGS_FILE, 'w') as f:
         yaml.dump(self.saved_settings, f, default_flow_style=False)
         f.close()   

   def animate(self, i):
      #ydata = self.line2d.get_ydata(False)
      #if len(ydata):
         #max = np.max(self.line2d.get_ydata(True))
         #min = np.min(self.line2d.get_ydata(True))
         #bottom, top = self.canvas.axes.get_ylim()

         #if max > top:
         #   self.canvas.axes.set_ylim(bottom, max+2.0)
         #   self.canvas.draw()
         #if min < bottom:
         #   self.canvas.axes.set_ylim(min-2.0, top)
         #   self.canvas.draw()
         #ydata[ydata <= self.POLAR_COORD_MIN] = self.POLAR_COORD_MIN-.0
           
      return self.line2d,

   def set_enable_all(self, enable):
      self.groupBox1.setEnabled(enable)
      self.groupBox2.setEnabled(enable)
      self.groupBox3.setEnabled(enable)
      self.groupBox4.setEnabled(enable)
      self.StartButton.setEnabled(enable)
      self.StopButton.setEnabled(not enable)

   @Slot()
   def set_figure_title(self, title):
      self.canvas.axes.set_title(title, va='bottom')
      self.canvas.axes.set_ylim(ymin=self.POLAR_COORD_MIN, ymax=self.POLAR_COORD_MAX)
      self.canvas.draw()
      
   @Slot()
   def save_figure(self, filename):
      if not os.path.isdir('save'): 
         os.makedirs('save')
           
      self.anim.pause()
      size = self.canvas.fig.get_size_inches()
      self.canvas.fig.set_size_inches(15, 15, forward=False)
      self.canvas.fig.savefig('save/' + filename + '.svg', format='svg', dpi=1000)
      self.canvas.fig.set_size_inches(size)
      self.anim.resume()

      array = np.array(self.line2d.get_data(True))
      array[0] = np.rad2deg(array[0])
      array = np.dstack(array)[0]
      np.savetxt('save/' + filename + '.csv', array, header='degree(°),gain(db)', fmt='%.4f,%.4f')

      #QMessageBox.information(self, 'Save Figure', 'Saving Complete', QMessageBox.Yes)

   @Slot()
   def checkbox_clicked(self, checked):
      if self.sender() == self.UseCalibCheckBox:
         self.CalibFileLineEdit.setEnabled(checked)
         self.OpenCalibFileButton.setEnabled(checked)
         self.saved_settings['use_calib'] = checked

   @Slot()
   def stop_button_clicked(self):
      self.meas_thread.requestInterruption()

   @Slot()
   def start_button_clicked(self):
      self.set_enable_all(False)
     
      if not self.check_settings():
         self.set_enable_all(True)
         return
      
      self.line2d.set_data([], [])
      self.meas_thread.start()

   @Slot(list) 
   def receive_pattern_data(self, data):
      self.line2d.set_data(data[0], data[1])

   @Slot()
   def thread_finished(self):
     self.set_enable_all(True)  

   @Slot()
   def meas_thread_error_message(self, string):
      self.error_message(string)

   @Slot()
   def text_edited(self, text):
      e = self.settings_table[self.sender()]
      if text != '':
         try:
            self.saved_settings[e[0]] = e[1](text)  
         except ValueError as e:
            pass
 
   @Slot()
   def index_changed(self, index):
      e = self.settings_table[self.sender()]
      self.saved_settings[e[0]] = e[1](self.sender().itemText(index))

   @Slot()
   def open_calib_file(self):
      filename = QFileDialog.getOpenFileName(self, 'Open Calibration File', '', 'YAML Files (*.yaml)')[0]
      self.saved_settings['calib_file'] = filename
      self.CalibFileLineEdit.setText(filename)

if __name__ == "__main__":
   app = QApplication(sys.argv)

   main_window = AnalyzerMainWindow()
   main_window.show()
   
   sys.exit(app.exec_())
