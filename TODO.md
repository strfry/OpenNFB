Towards Domain Specific Language:

*) Latency Measuring Test Case
*) Block class as Functor(was: Implement Block class)
*) Threshold block with widget


## OpenBCI device

* Uses no openbci.org code
* Automatic restarts
* Sync Unit (timestamps)
* Latency correction


### Custom Firmware

* 30 Hz Aliasing bug
* Customize Sampling Rate (fewer channels)
* DSP on site (STM32)
* Grow Light pulsing


Design Decisions:

- OutputPort's are buffering stuff themselves, as requested by InputPort's on connection

- Source Blocks (Channels) can be requested through the Context
	* Sources are just a output port, no special class
	* Context has the source ports
	* Sources are identified through names, like 'Channel 1'
- There is a device class, that controls the hardware driver, and can log data for replay/pause/seek functionality
- Device and Context are bound together via signals

- Recording class is named 'History'



BUGS:
* (OpenBCI link becomes unreliable sometimes) not seen anymore -> Detect link problems and implement automatic restarting

TODO:
* Limit Error message (and trace() feature)
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
* Spectrogram widget
* Spectrogram (bar mode)
* Look into GNURadio
* Simple plot setup and filter bands
* Use WAV files everywhere
*

Live Coding:
* Use reload(), del dependencies from sys.modules

DSP:
* Wavelet transforms for ECG analysis

Widgets:
* Scrolling Plot / Oscillosope
* Fire animation

Hardware:
* Light & Sound Box


DSL Features:
============
Blocks:

* Source 
	- Wraps OpenBCI and WAV replay (Extra class/instance option for explicit replays)
* (Random Noise)


Transform:

* Filter (configurable between IIR and FIR)
- BandPass, Lo/Hi-Pass, Notch
* Threshold
* (FFT)
* (Wavelet transform)


Output:
* Oscilloscope
* Spectral analyzer



* Object oriented
* Channel -> device class
* single buffer length across filter chain
* Signal class:
	- Controls buffer length
	- Transports side channel data (for example Threshold)
	- Can transport transforms?
	- update mechanisms
	- decide: static or dynamic per-sample processing?
		static:
			- need to overload all kinds of operations (maybe derive from np.array?)
		dynamic:



* Save configs to .config file (with ConfigParser?)
