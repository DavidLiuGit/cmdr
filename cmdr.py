#!/bin/python3

# standard imports
from os import path
import struct
from sys import stderr
import signal

# utils
import cmdr_utils
import cmdr_funcs

# library imports
from porcupine import Porcupine
from cheetah import Cheetah
import pyaudio



def init_porcupine ( cfg ):
	"""Set up Porcupine params, and return an instance of Porcupine"""
	# determine paths to Porcupine binaries
	PORCUPINE_ROOT_PATH = cfg['root_path']
	porcupine_lib_path = path.join ( PORCUPINE_ROOT_PATH, cmdr_utils.rel_library_path() )
	porcupine_model_file_path = path.join ( PORCUPINE_ROOT_PATH, cfg['lib_path'] )

	# these files are the optimized and encoded keyword triggers
	porcupine_kw_file_ext = cmdr_utils.porcupine_keyword_file_extension()
	porcupine_keyword_file_paths = [
		path.join ( 
			PORCUPINE_ROOT_PATH, 
			cfg['keywords']['path'], 
			"%s_%s.ppn" % (kw['prefix'], porcupine_kw_file_ext) 
		) for kw in cfg['keywords']['list']
	]

	# sensitivity for each keyword in the above list; higher = more false positives
	# float values, ranging from 0 - 1
	porcupine_kw_sensitivities = [ 
		kw['sensitivity'] for kw in cfg['keywords']['list']
	]

	# initialize a Porcupine instance and return it
	return Porcupine ( 
		porcupine_lib_path, 
		porcupine_model_file_path, 
		keyword_file_paths=porcupine_keyword_file_paths, 
		sensitivities=porcupine_kw_sensitivities
	)



def init_cheetah ( cfg ):
	"""Set up Cheetah params, and return an instance of Cheetah"""
	root_path = cfg['root_path']
	lib_path = path.join ( root_path, cfg['lib_path'] )
	acoustic_model_path = path.join ( root_path, cfg['acoustic_model_path'] )
	language_model_path = path.join ( root_path, cfg['language_model_path'] )
	license_path = path.join ( root_path, cfg['license_path'] )

	# init and return
	return Cheetah (
		lib_path, acoustic_model_path,
		language_model_path, license_path
	)



def init_input_audio_stream ( handler_instance, device=None ):
	"""Init and return audio stream (pyaudio)"""
	pa = pyaudio.PyAudio()
	return pa.open(
		rate=handler_instance.sample_rate,
		channels=1,
		format=pyaudio.paInt16,
		input=True,
		frames_per_buffer=handler_instance.frame_length,
		input_device_index=device
	)



def break_loop (signal, frame):
	global interrupted
	if interrupted:
		exit(0)			# if interrupt flag already set, exit as normal
	interrupted = True	# otherwise, set the interrupt flag
signal.signal(signal.SIGINT, break_loop)
# signal.signal(signal.SIGSTOP, break_loop)
interrupted = True


def handle_keyword_detected ( cmdr_state, kw_index, cheetah ):
	"""Handle Porcupine keyword detection event"""
	try:
		keyword_obj = cmdr_state.config['porcupine']['keywords']['list'][kw_index]
	except:
		print ( "Error: keyword index out of bounds", file=stderr, flush=True )

	print ( 
		"Keyword detected!", 
		kw_index, 
		keyword_obj['title'] )

	if kw_index == 3:
		active_process = cmdr_funcs.play_despacito()
		cmdr_state.active_process = active_process
	else:
		audio_stream = init_input_audio_stream ( cheetah )
		print (cheetah.frame_length)
		global interrupted
		interrupted = False
		while True:
			pcm = audio_stream.read ( cheetah.frame_length )
			pcm = struct.unpack_from ("h" * cheetah.frame_length, pcm)
			cheetah.process(pcm)

			if interrupted:
				break

		print ( cheetah.transcribe() )
		# global interrupted
		interrupted = True




def main ():
	# determine platform & machine
	platform = cmdr_utils.get_platform(True)
	machine = cmdr_utils.get_machine(True)

	# track the state, including any active (background) process
	state = cmdr_utils.CmdrState()

	# init Porcupine
	porcupine = init_porcupine ( state.config['porcupine'] )

	# init Cheetah
	cheetah = init_cheetah ( state.config['cheetah'] )

	# init audio stream (pyaudio)
	audio_stream = init_input_audio_stream(porcupine)

	# listen for keyword in a loop
	while True:
		pcm = audio_stream.read(porcupine.frame_length)
		pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

		keyword_index = porcupine.process(pcm)
		# if a keyword is detected
		if keyword_index >= 0:
			# if there is an active background process, kill it
			if state.active_process:
				state.active_process.terminate()

			# porcupine keyword detection event
			handle_keyword_detected ( state, keyword_index, cheetah )


	# cleanup
	cleanup ( porcupine )



def cleanup ( porcupine ):
	porcupine.delete()


if __name__ == "__main__":
	main()
