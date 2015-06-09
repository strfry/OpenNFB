import sys
import struct
from time import sleep

class BDFReader(object):
  SAMPLE_RATE = 250
  NUM_CHANNELS = 8

  def __init__(self, fileobj):
    self.fileobj = fileobj
    data = fileobj.read(256)

    # Ignore header, and assume we open our own files

    assert("\xffBIOSEMI" == data[0:8])

    header_len = int(data[184:192].strip())

    assert float(data[244:252].strip()) == 1.0

    assert int(data[252:256].strip()) == 8 # Number of channels
    
    fileobj.read(header_len - 256)

    self.read_buffer = []
    self._read_into_buffer()

  def readPacket(self):
    if len(self.read_buffer) == 0:
      self._read_into_buffer()

    if len(self.read_buffer) > 0:
      return self.read_buffer.pop(0)

  def start_streaming(self, handler):
    assert len(self.read_buffer) > 0
    eof = False
    while not eof:
      sleep(1.0 / self.SAMPLE_RATE)

      packet = self.readPacket()

      if packet:        
        handler(self.read_buffer.pop(0))
      else:
        eof = True
            

  def _read_into_buffer(self):
    block_size = 3 * self.SAMPLE_RATE * 8
    block = self.fileobj.read(block_size)
    
    if len(block) < block_size:
      return True

    for sample in range(self.SAMPLE_RATE):
      packet = ()
      for channel in range(self.NUM_CHANNELS):
            idx = (channel * self.SAMPLE_RATE + sample) * 3
            chunk = block[idx:idx+3]
            packet += struct.unpack('<i', chunk + ('\0' if chunk[2] < 128 else '\xff'))
      #print packet
      self.read_buffer += (packet,)
      
    return False


if __name__ == '__main__':
  fileobj = file(sys.argv[1], 'rb')
  bdf = BDFReader(fileobj)
  
  def handler(packet):
    print packet

  bdf.start_streaming(handler)

  
