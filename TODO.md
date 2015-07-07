Towards Domain Specific Language:

1) Build a simple test bench for Context
2) Implement Block class
3) Threshold block with widget
4) OpenBCI device with source blocks/ports



BUGS:
* (OpenBCI link becomes unreliable sometimes) not seen anymore -> Detect link problems and implement automatic restarting

TODO:
* Make a simple threshold widget
* Make a Block class, containing InPort's and OutPort's
	connect ports with connect() like external syntax
	InPorts require buffer lengths, OutPorts do the buffering?
	Give blocks a name, so they can store their config in a separate file in Python object notation
	Support for meta-data, like thresholds, signal name etc.
* Look into GNURadio, especially the processing and sample forwarding architecture


Instrument Control
* Generate MIDI events, control volume, pitch, other filters...
* Take a look at OSC (pyosc) - done, better use MIDI for ableton


Recording Features
* GUI Frame with notion of a "session", and record/playback functionality
* Start/Stop/Pause and maybe looping
* Freely usable WAV file record and playback blocks
* Buffer reset/refill feature
* Support for seeking

Live Coding:
* Use reload(), del dependencies from sys.modules

DSP:
* Wavelet transforms for ECG analysis

Widgets:
* Scrolling Plot / Oscillosope
* Fire animation

Hardware:
* Light & Sound Box




