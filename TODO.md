BUGS:
* OpenBCI link becomes unreliable sometimes

TODO:
* Make a simple threshold widget
* Clean up band filter code
* Spectrogram
* Look into GNURadio
* Take a look at OSC (pyosc)
* Simple plot setup and filter bands
* Use WAV files everywhere

Live Coding:
* Use reload(), del dependencies from sys.modules

DSP:
* Wavelet transforms for ECG analysis

Widgets:
* Scrolling Plot / Oscillosope
* Spectrogram (based on Multiple Plots benchmark example)
* Fire animation

Hardware:
* Light & Sound Box


DSL Features:

* Object oriented
* Channel -> device class
* single buffer length across filter chain
* Signal class controls buffer length, and transports side-channel data (threshold height for example)
* Save configs to .config file (with ConfigParser?)



GUI quirks:
* Start/Stop/Rewind functionality (automatic looping)
