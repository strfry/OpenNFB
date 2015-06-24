import sys
import wave
from os.path import splitext
from bdf import BDFReader
import struct

filename = sys.argv[1]
base, ext = splitext(filename)


wavfile = wave.open(base + '.wav', 'w')
wavfile.setnchannels(1)
wavfile.setsampwidth(3)
wavfile.setframerate(250)

reader = BDFReader(file(filename, 'rb'))

packet = reader.readPacket()

while packet:
  data = struct.pack('=i', packet[0])
  wavfile.writeframesraw(data[1:])
  packet = reader.readPacket()

wavfile.close()

print "foo"
