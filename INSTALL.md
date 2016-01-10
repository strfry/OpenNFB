OSX:

pip install pyqtgraph pyside pyserial
brew install pyside

see http://bruteforce.gr/bypassing-clang-error-unknown-argument.html
ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install traits traitsui


For OSC support:
pip install PyOSC


Install GnuRadio from this tap:
https://github.com/metacollin/homebrew-gnuradio

Before installing, read the section on the python version you want to link with.
The GnuRadio compilaton takes quite some time, and if you discover that you want to link with your systems python, you have to wait again!

  brew tap metacollin/gnuradio
  brew install gnuradio
  

GnuRadio links against the python implementation provided by homebrew.
That means OpenNFB has to be executed with that python version, otherwise it will crash in the GnuRadio libs.

There are 3 solutions to alleviate this:
1) Always execute with explicit path:
  /usr/local/Cellar/python/2.7.10_2/bin/python gnuradio_protocol.py

2) Change system path to use Homebrews python by default
http://stackoverflow.com/questions/5157678/python-homebrew-by-default

3) Compile GnuRadio against systems python
Refer to the end of https://github.com/metacollin/homebrew-gnuradio
