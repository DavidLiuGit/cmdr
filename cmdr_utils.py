# cmdr utilities
import importlib, importlib.util
import platform
import os
from json import load as json_load
from pprint import pprint
from enum import Enum
from sys import stderr



class Cmdr:

	class CmdrStateEnum(Enum):
		IDLE = -1					# doing nothing
		PORCUPINE_LISTENING = 1		# Porcupine: listening for keyword
		CHEETAH_LISTENING = 100		# Cheetah: listening to input and processing
		CHEETAH_TRANSCRIBING = 101	# Cheetah: computing transcription
		ACTIVE_PROCESS = 2			# Another process was launched and is currently running


	def __init__ (self, config_file="config.json"):
		self.config = self.load_config(config_file)	# read in config file, config.json
		self.active_process = None
		self.state = self.CmdrStateEnum.IDLE


	def load_config ( self, file ):
		"""Read in the JSON config file as a dict for easy reference"""
		with open(file) as f:
			cfg = json_load(f)
		print ( "Cmdr version ", cfg["version"] )
		return cfg


	@property
	def state (self): return self._state
	
	@state.setter
	def state (self, val):
		try: self._state = self.CmdrStateEnum(val)
		except:	print ("Error: invalid CmdrStateEnum", file=stderr)




# class CmdrConfig:
# 	def __init__ ( self, file="config.json" ):
# 		"""Read in the JSON config file as a dict for easy reference"""
# 		with open(file) as f:
# 			self = json_load(f)
# 		print ( "Cmdr version ", self["version"] )



def module_from_file ( module_name, file_path ):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_platform ( lower=False ):
	"""Return the string detailing the current machine's platform (e.g. Linux, Mac, Windows); set `lower=True` to get lower case"""
	return platform.system() if not lower else platform.system().lower()

def get_machine ( lower=False ) :
	"""Return the string detailing the current machine's architecture (e.g. i386, x86_64); set `lower=True` to get lower case"""
	return platform.machine()  if not lower else platform.machine().lower()


def rel_library_path():
	system = platform.system()
	machine = platform.machine()

	if system == 'Darwin':
		return 'lib/mac/%s/libpv_porcupine.dylib' % machine
	elif system == 'Linux':
		if machine == 'x86_64' or machine == 'i386':
			return  'lib/linux/%s/libpv_porcupine.so' % machine
		elif machine.startswith('arm'):
			# NOTE: This does not need to be fast. Use the armv6 binary.
			return  'lib/raspberry-pi/arm11/libpv_porcupine.so'
	elif system == 'Windows':
		if platform.architecture()[0] == '32bit':
			return  'lib\\windows\\i686\\libpv_porcupine.dll'
		else:
			return  'lib\\windows\\amd64\\libpv_porcupine.dll'

	raise NotImplementedError('Porcupine is not supported on %s/%s yet!' % (system, machine))


def porcupine_keyword_file_extension():
	system = platform.system()
	machine = platform.machine()

	if system == 'Linux' and (machine == 'x86_64' or machine == 'i386'):
		return 'linux'
	elif system == 'Darwin':
		return 'mac'
	elif system == 'Linux' and machine.startswith('arm'):
		return 'raspberrypi'
	elif system == 'Windows':
		return 'windows'

	raise NotImplementedError('Porcupine is not supported on %s/%s yet!' % (system, machine))



def abs_list_avg ( input_list ):
	"""Given an input list of numbers, return the absolute value average of the list"""
	sum = 0
	for i in input_list:
		sum += abs(i)
	return sum / len(input_list)
