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

## Hardware:

I currently work with the OpenBCI (http://www.openbci.com), in particular the 8 Bit version with 8 Channels.
While the software should ideally be modular enough to support other devices, i do not think about a hardware abstraction layer at this point.

At this point it should be noted that the file open_bci_v3.py comes from the original OpenBCI_Python project: https://github.com/OpenBCI/OpenBCI_Python

## Functionality

### Recording

The script record_bdf.py connects to the OpenBCI and writes a file in BDF File Format (http://www.biosemi.com/faq/file_format.htm).
This format was chosen because it supports 24 bit resolution and can easily be opened with EDFBrowser (http://www.teuniz.net/edfbrowser/) for verification.

### Playback

Recorded BDF files can be visualized with liveplot.py.
This is my current setup for developing filters without the need to stick electrodes to my scalp each time.

### Live Visualization

TBD



## OSX Workaround

If you want to test this on OSX, mind the FTDI Driver fix: https://github.com/OpenBCI/Docs/blob/master/tutorials/09_Mac_FTDI_Driver_Fix.md
But beware, it sometimes freezes my Mac (or only the input devices), which can lead to data loss.



# Glossary of central Concepts

## Flow

A Flow is a setup of processing Blocks, like Channels, Filters, Triggers and Oscilloscopes.
This is the equivalent to the design file in software like BioExplorer, but written in Python.
Flows are reloaded automatically when their corresponding source files change.

A flow can have an associated config file, that can be
used to outsource parametric settings,
and store settings made in the GUI of interactive
Blocks()

In GNURadio, the equivalent to this might be the top block.
It is agnostic the specific hardware, and whether it is 
feeded by a recording or running live.

So this means a Flow is a Block too?

## Context

The 'runtime', that takes care of examining the flowchart
for cyclicality. This part is responsible for 'driving'
the Flow pipeline.
Raw sensor data is logged into a history, and flushed
through the Flow on demand (reload).
So this classes lifespan reaches across reloads of Flow
sources.


## Block

Parent class for all source, processing and display elements. A block can have Inputs, Outputs and config parameters, which all share the attribute namespace.


## Input

A member variable of blocks that can be assigned 
to outputs of other blocks.
Inputs can specify how much past buffer they need, which is automatically provided by the connected output.
This is also used to calculate the maximum latency to
flush the Flow pipeline on reloads.
Inputs that specify a default value do not need to be
connected to an output in order for the Block to function.

## Output

The actual signal class. Like Block, it can contain
arbitrary information as attribute. This can be used for
meta-data, like a name and color the signal should be
painted with when it is passed into an Oscilloscope
Outputs carry a buffer of past values, whose exact size
is determined by the inputs it is assigned to.
On each processing step, a number of new samples is
appended.
It also contains utility functions for detecting edges
in the new sample chunk, and thus use also use it for trigger signals.



