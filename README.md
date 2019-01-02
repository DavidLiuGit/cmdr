# Cmdr

Cmdr is an offline voice assistant, powered by the [libraries](https://github.com/Picovoice) created by [Picovoice](https://picovoice.ai/). These libraries provide functionalities such as:

1. wake-word detection (Porcupine)
2. speech-to-text (Cheetah)



## Usage
Cmdr has been tested for use on Linux x86 machines, running Ubuntu, for English speakers.
* Install dependencies with pip
	```bash
	pip install -r requirements.txt
	```
* Cmdr uses [SpaCy](https://spacy.io) for NLP. SpaCy and it's dependencies can be installed with pip in the step above. Models for SpaCy can be installed with the following commands:
	```bash
	python3 -m spacy download en
	```
* Run cmdr
	```bash
	python3 cmdr.py
	```


## Features

![Common uses for voice assistants](https://ei.marketwatch.com/Multimedia/2018/01/18/Photos/ZH/MW-GC002_voice__20180118140125_ZH.jpg?uuid=fb25668e-fc81-11e7-9b31-9c8e992d421e )