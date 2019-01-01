#!/bin/python3

# standard imports
from os import path
import struct
from sys import stderr
import signal
from time import sleep
from math import floor

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
		rate=handler_instance.sample_rate,	# sample rate (samples/second)
		channels=1,							# single channel input
		format=pyaudio.paInt16,				# 16-bit encoding
		input=True,							# use as input
		frames_per_buffer=handler_instance.frame_length,	# samples/buffer
		input_device_index=device			# leave as None to use sys default input device
	)	# buffers/sec = (frames/sec) * (buffers/frames)


interrupted = True
def break_loop (signal, frame):
	"""
	Set the `interrupted` flag to True if it not already True  
	If `interrupted` is already set, gracefully exit program as normal.  
	The `interrupted` flag should be checked by an infinite loop to conditionally break
	"""
	global interrupted
	if interrupted:
		exit(0)			# if interrupt flag already set, exit as normal
	interrupted = True	# otherwise, set the interrupt flag
# use `break_loop` to handle SIGINT (ctrl+C)
signal.signal(signal.SIGINT, break_loop)



def cheetah_listen (cmdr_state, audio_stream, cheetah):
	"""Listen to audio stream until interrupted, then transcribe"""
	# listen to command until interrupted (SIGINT) or user stops talking
	global interrupted
	interrupted = False
	while not interrupted:
		pcm = audio_stream.read ( cheetah.frame_length )
		pcm = struct.unpack_from ("h" * cheetah.frame_length, pcm)
		print ( floor(cmdr_utils.abs_list_avg(pcm)), end=", ", flush=True )
		cheetah.process(pcm)

	# set the interrupted flag to True (probably redundant)
	interrupted = True

	# transcribe with cheetah; return results
	return cheetah.transcribe()



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
		cmdr_state.state = cmdr_state.CmdrStateEnum.ACTIVE_PROCESS
		cmdr_state.active_process = active_process
	elif kw_index == 4:
		cmdr_state.active_process = cmdr_funcs.play_audio_background("assets/music/untitled.mp3")
		cmdr_state.state = cmdr_state.CmdrStateEnum.ACTIVE_PROCESS
	else:
		# init an audio input stream, using the mic input, with cheetah's params
		audio_stream = init_input_audio_stream ( cheetah )

		# sleep for 0.2 seconds to avoid reading in noise from the wake word
		sleep(0.2)

		# listen and transcribe from input stream
		cmdr_state.state = cmdr_state.CmdrStateEnum.CHEETAH_LISTENING
		transcript = cheetah_listen (cmdr_state, audio_stream, cheetah)
		print (transcript)
		





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

	# init audio stream (pyaudio) for Porcupine
	audio_stream = init_input_audio_stream(porcupine)
	state.state = state.CmdrStateEnum.PORCUPINE_LISTENING	# Porcupine begin listening

	# listen for keyword in a loop
	while True:
		# from the input audio stream, read in a the specified number of frames
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
			state.state = state.CmdrStateEnum.PORCUPINE_LISTENING


	# cleanup
	cleanup ( porcupine )



def cleanup ( porcupine ):
	porcupine.delete()


if __name__ == "__main__":
	main()
