OpenNFB
==============

A Neurofeedback software approach based on Python and Qt/pyqtgraph.
It is ment for programmers, because it does not try to provide a visual programming language, like BrainBay/BioEra/BioExplorer,
so it is only sutable for those who do not fear source code and the command line.


## Dependencies:

* Python 2.7 or later (https://www.python.org/download/releases/2.7/)
* Numpy 1.7 or later (http://www.numpy.org/)
* SciPy
* PySide
* PyQtGraph (http://www.pyqtgraph.org/)
* traits

## Hardware:

I currently work with the OpenBCI (http://www.openbci.com), in particular the 8 Bit version with 8 Channels.
While the software should ideally be modular enough to support other devices, i do not think about a hardware abstraction layer at this point.

At this point it should be noted that the file open_bci_v3.py comes from the original OpenBCI_Python project: https://github.com/OpenBCI/OpenBCI_Python

## Functionality

### Recording

The script record_bdf.py connects to the OpenBCI and writes a file in BDF File Format (http://www.biosemi.com/faq/file_format.htm).
This format was chosen because it supports 24 bit resolution and can easily be opened with EDFBrowser (http://www.teuniz.net/edfbrowser/) for verification

### Playback

Recorded BDF files can be visualized with replay_flow.py.
This is my current setup for developing filters without the need to stick electrodes to my scalp each time.

#### Usage

Test the ekg-drum flow like this:

    python replay_flow.py ekg-drum recordings/ekg_strfry_23.06.15.bdf

### Live Visualization

TBD



## OSX Workaround

If you want to test this on OSX, mind the FTDI Driver fix: https://github.com/OpenBCI/Docs/blob/master/tutorials/09_Mac_FTDI_Driver_Fix.md
But beware, it sometimes freezes my Mac (or only the input devices), which can lead to data loss.
