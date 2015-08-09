life filter adjustment (SMR frequency)
automatic log file naming (only specify username)

## Filters and such

- Graphic autoscale/normalizing feature (based on marking a good range)
- Peak filter
- use detrend?
- Find out of IIR filters work, and use correctly (maybe higher orders will work then?)
- 

## Traits semantics

* Disallow assignment of undeclared traits
* Input trait for non-signal stuff, default value
* constructor arguments, automatable? (for using init())
* process call does not work for collections of Input()
* Simplify threshold into one mode, with 0 treshold deactivating sides
* set colors on filters
* Threshold.passfail should be standard output

## Towards Domain Specific Language:

*) Think thoroughly about semantics of Signal
	- Sample rate, nyquist
	- Problem field of 'shadow' signals, that have same content but different metadata
	- combine append/process

*) Reverse Control flow, start processing from output blocks
	Look at pyo, visitor pattern

	- Enumerate all output Blocks
		* Output blocks register at some instance (Context)
		* Output blocks derive from a class OutputBlock
	- Find out how much samples are to be processed
	- Walk through the chain and process
	- Cache results that are in path for other output blocks

*) Latency Measuring Test Case
*) Threshold block with widget
*) Module structure, naming
*) Fix filter buffer size

## Dependencies

* Move away from rtmidi2 to something more standard, maybe pypm
* investigate chaco to replace pyqtgraph
* take a look at pyface

## OpenBCI device

* Uses no openbci.org code
* Automatic restarts
* Sync Unit (timestamps)
* Latency correction

* Proper unit conversion to float/milliVolts

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
* Buffer length request feature for Input() port
* Give blocks a name, so they can store their config in a separate file in Python object notation

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
* Use WAV files everywhere
*


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
* Think of a way to register 'virtual' sources to Context

Transform:

* Filter (configurable between IIR and FIR)
- BandPass, Lo/Hi-Pass, Notch
* Threshold
* (FFT)
* (Wavelet transform)


Output:
* Oscilloscope
* Spectral analyzer

* single buffer across filter chain (an idea from pyo, allow in-place processing)
* Signal class:
	- Controls buffer length
	- Transports side channel data (for example Threshold)
	- Can transport transforms (frequency domain)?



* Save configs to .config file (with ConfigParser?)


Rewriting or patching the OpenBCI firmware is on my agenda for 2 reasons:
1) There is this bug, which sometimes introduces an aliasing artefact at 30 Hz, much like the 50 Hz mainline noise. This is probably a misconfiguration of the ADS1299, maybe the wrong low pass filter at the input stage is selected.
2) I want to optionally use higher sample rates than 250 Hz (the ADS1299 supports up to 16 kHz). This might be possible by deactivating some channels, to get everything through the rate limited Bluetooth line. Higher sample rates are interesting for examining lambda waves (above gamma, starting from 150 Hz), and EMG analysis, where signals up to 1 kHz are told to be found.
