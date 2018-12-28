# std imports
from subprocess import Popen, DEVNULL




def play_despacito ():
	"""Does exactly what it sounds like"""
	despacito_path = "assets/music/despacito.mp3"
	return play_audio_background ( despacito_path )


def play_audio_background ( audio_file_path ):
	"""
	Using `ffplay`, a `ffmpeg` utility, to play audio in background.  
	Return the process object so that it can be manipulated (i.e. send SIGINT, SIGTERM)
	"""
	cmdlist = [ 'ffplay', '-nodisp', audio_file_path ]
	print ( ' $', ' '.join(cmdlist) )
	return Popen ( cmdlist, stdout=DEVNULL )