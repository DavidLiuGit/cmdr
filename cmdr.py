#!/bin/python3

# standard imports
from os import path
import struct
from subprocess import Popen

# utils
import cmdr_utils

# library imports
from porcupine import Porcupine
import pyaudio
# from play_despacito import play_audio_file



def init_porcupine ():
	"""Set up Porcupine params, and return an instance of Porcupine"""
	PORCUPINE_ROOT_PATH = "Porcupine"
	porcupine_lib_path = path.join ( "Porcupine", cmdr_utils.rel_library_path() )
	porcupine_model_file_path = path.join ( PORCUPINE_ROOT_PATH, "lib/common/porcupine_params.pv" )
	porcupine_kw_file_ext = cmdr_utils.porcupine_keyword_file_extension()
	porcupine_keyword_file_paths = [		# these files are the encoded keywords
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "hey_alexa_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "porcupine_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "buttery_chocolate_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "ill_be_back_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "play_despacito_%s.ppn" % porcupine_kw_file_ext ),
	]
	porcupine_kw_sensitivities = [ 0.4, 0.25, 0.4, 0.45, 0.666 ]

	return Porcupine ( 
		porcupine_lib_path, 
		porcupine_model_file_path, 
		keyword_file_paths=porcupine_keyword_file_paths, 
		sensitivities=porcupine_kw_sensitivities
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



def play_despacito ():
	"""Does exactly what it sounds like"""
	despacito_path = "assets/music/despacito.mp3"
	cmdlist = [ 'ffplay', '-nodisp', despacito_path ]
	Popen ( cmdlist )



def main ():
	# determine platform & machine
	platform = cmdr_utils.get_platform(True)
	machine = cmdr_utils.get_machine(True)

	# init Porcupine
	handle = init_porcupine()

	# init audio stream (pyaudio)
	audio_stream = init_input_audio_stream(handle)

	# listen for keyword
	while True:
		# pcm = get_next_audio_frame()
		pcm = audio_stream.read(handle.frame_length)
		pcm = struct.unpack_from("h" * handle.frame_length, pcm)

		keyword_index = handle.process(pcm)
		if keyword_index >= 0:
			# detection event logic/callback
			print ( "keyword detected!", keyword_index )

		if keyword_index == 4:
			play_despacito()		# kek



	# cleanup
	cleanup ( handle )



def cleanup ( porcupine ):
	porcupine.delete()


if __name__ == "__main__":
	main()


print ( "hello cmdr" )