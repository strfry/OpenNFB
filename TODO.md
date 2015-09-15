# OpenBCI Driver
- Automatic restarting if stream stops
- Handle missing packets
- Switch off common reference (noise)
- Impedance checking GUI
- Unit conversion to µV
## Firmware rewrite (?)
  change samplerate


# Live Control Features
Training frequency selection widget


# Recording Tool
automatic log file naming (only specify username)

## Filters and such

- Graphic autoscale/normalizing feature (based on marking a good range)
- Peak filter
- Find out of IIR filters work, and use correctly (maybe higher orders will work then?)
- Artifact Rejection

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


Design Decisions:

- OutputPort's are buffering stuff themselves, as requested by InputPort's on connection

- Source Blocks (Channels) can be requested through the Context
	* Sources are just a output port, no special class
	* Context has the source ports
	* Sources are identified through names, like 'Channel 1'
- There is a device class, that controls the hardware driver, and can log data for replay/pause/seek functionality
- Device and Context are bound together via signals

- Recording class is named 'History'



TODO:
* Limit Error message (and trace() feature)
* Make a simple threshold widget
* Buffer length request feature for Input() port
* Give blocks a name, so they can store their config in a separate file in Python object notation


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
* Light & Sound Box (Grow light)


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
* single buffer across filter chain (an idea from pyo, allow in-place processing)
* Signal class:
	- Controls buffer length
	- Transports side channel data (for example Threshold)
	- Can transport transforms (frequency domain)?



* Save configs to .config file (with ConfigParser?)


