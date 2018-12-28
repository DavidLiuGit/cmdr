#!/bin/python3

# standard imports
from os import path
import struct

# utils
import cmdr_utils
import cmdr_funcs

# library imports
from porcupine import Porcupine
import pyaudio



def init_porcupine ():
	"""Set up Porcupine params, and return an instance of Porcupine"""
	PORCUPINE_ROOT_PATH = "Porcupine"
	porcupine_lib_path = path.join ( "Porcupine", cmdr_utils.rel_library_path() )
	porcupine_model_file_path = path.join ( PORCUPINE_ROOT_PATH, "lib/common/porcupine_params.pv" )
	porcupine_kw_file_ext = cmdr_utils.porcupine_keyword_file_extension()
	porcupine_keyword_file_paths = [		# these files are the encoded keywords
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "buttery_chocolate_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "hey_monica_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "monica_%s.ppn" % porcupine_kw_file_ext ),
		path.join ( PORCUPINE_ROOT_PATH, "keywords", "play_despacito_%s.ppn" % porcupine_kw_file_ext ),
	]
	porcupine_kw_sensitivities = [ 0.25, 0.4, 0.4, 0.666 ]

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




def handle_keyword_detected ( cmdr_state, kw_index ):
	print ( "keyword detected!", kw_index )

	if kw_index == 3:
		active_process = cmdr_funcs.play_despacito()
		cmdr_state.active_process = active_process



def main ():
	# determine platform & machine
	platform = cmdr_utils.get_platform(True)
	machine = cmdr_utils.get_machine(True)

	# init Porcupine
	handle = init_porcupine()

	# init audio stream (pyaudio)
	audio_stream = init_input_audio_stream(handle)

	# track the state, including any active (background) process
	state = cmdr_utils.CmdrState()

	# listen for keyword in a loop
	while True:
		pcm = audio_stream.read(handle.frame_length)
		pcm = struct.unpack_from("h" * handle.frame_length, pcm)

		keyword_index = handle.process(pcm)
		# if a keyword is detected
		if keyword_index >= 0:
			# if there is an active background process, kill it
			if state.active_process:
				state.active_process.terminate()

			# handle keyword detection event
			handle_keyword_detected ( state, keyword_index )


	# cleanup
	cleanup ( handle )



def cleanup ( porcupine ):
	porcupine.delete()


if __name__ == "__main__":
	main()
