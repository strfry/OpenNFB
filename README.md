OpenNFB
==============

A Neurofeedback software approach based on Python and Qt5/pyqtgraph
It is ment for programmers, because it does not try to provide a visual programming language, like BrainBay/BioEra/BioExplorer,
so it is only sutable for those who do not fear source code and the command line.


## Dependencies:

* Python 3.1 or later
* Numpy 1.7 or later
* SciPy
* PyQt5
* PyQtGraph (you need github:develop branch for PyQt5 support)
* traits

## Hardware:

I currently work with the OpenBCI (http://www.openbci.com), in particular the 8 Bit version with 8 Channels.
While the software should ideally be modular enough to support other devices, i do not think about a hardware abstraction layer at this point.

At this point it should be noted that the file open_bci_v3.py comes from the original OpenBCI_Python project: https://github.com/OpenBCI/OpenBCI_Python

There is experimental support for the other "Open-BCI", also called Brain-Duino (http://www.psychiclab.net/IBVA/kit1.html). Note that the samplerate is samplerate is still hard-coded everywhere, and some of the math will be wrong for the default rate of 512 Hz.

## Functionality

### Servers

The data acquisition sources are called 'server'. There is replay_server.py for playing back a BDF recording, and brainduino_server.py and openbci_server.py to do live hardware feedback.
Replays are very useful for development without attaching electrodes each time.

### Recording

This Information is deprecated, currently there is no recording facility:
The script record_bdf.py connects to the OpenBCI and writes a file in BDF File Format (http://www.biosemi.com/faq/file_format.htm).
This format was chosen because it supports 24 bit resolution and can easily be opened with EDFBrowser (http://www.teuniz.net/edfbrowser/) for verification

### Feedback

### Live Visualization

TBD



## OSX Workaround

If you want to test this on OSX, mind the FTDI Driver fix: https://github.com/OpenBCI/Docs/blob/master/tutorials/09_Mac_FTDI_Driver_Fix.md
But beware, it sometimes freezes my Mac (or only the input devices), which can lead to data loss.
