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
    assert(b"\xffBIOSEMI" == data[0:8])

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
            packet += struct.unpack('<i', chunk + (b'\0' if chunk[2] < 128 else b'\xff'))
      #print packet
      self.read_buffer += (packet,)
      
    return False


  
def pad(s, l):
    s = s[0:l]
    diff = l - len(s)
    s = s + " " * diff
    return s

class BDFWriter(object):
    SAMPLE_RATE = 250

    def __init__(self, num_channels):
        self.num_channels = num_channels
        self.samples = [list() for _ in range(num_channels)]
        pass

    def append_sample(self, samples):
        assert len(samples) == self.num_channels
        for idx, sample in enumerate(samples):
            self.samples[idx].append(sample)


    def write_file(self, filehandle):
        self._write_header(filehandle)

        start = filehandle.tell()

        sample_idx = 0

        while sample_idx < len(self.samples[0]):
            for channel in self.samples:
                for sample in channel[sample_idx: sample_idx + self.SAMPLE_RATE]:
                    filehandle.write(chr(sample & 0xff))
                    filehandle.write(chr((sample >> 8) & 0xff))
                    filehandle.write(chr((sample >> 16) & 0xff))
            sample_idx += self.SAMPLE_RATE

            diff = sample_idx - len(self.samples[0])

            start = filehandle.tell()

            if diff > 0:
                filehandle.write("\0" * diff * 3 * self.num_channels)

    # Write BDF Header
    # Based on: http://www.biosemi.com/faq/file_format.htm
    def _write_header(self, f):
        assert isinstance(f, file)
        f.write("\xffBIOSEMI")

        f.write(pad("Local Subject Identification", 80))
        f.write(pad("Local Recording Identification", 80))

        # TODO: Write current datetime
        f.write("25.05.15")
        f.write("15.26.42")

        header_len = (self.num_channels + 1) * 256  # Derived from EDFBrowser error message
        f.write(pad(str(header_len), 8))

        f.write(pad("24BIT", 44))

        num_records = (len(self.samples[0]) + self.SAMPLE_RATE - 1) / self.SAMPLE_RATE
        f.write(pad(str(num_records), 8))   # Number of data records
        f.write(pad("1.0", 8))    # Duration of a data record, in seconds

        f.write(pad(str(self.num_channels), 4))     # Number of channels

        channel_headers = [self._gen_channel_header(channel) for channel in range(self.num_channels)]

        try:
            while True:
                for channel in channel_headers:
                    f.write(channel.next())
                    pass
        except StopIteration:
            pass



    def _gen_channel_header(self, channel):
        gain = 24

        digital_max = 2**23 - 1
        digital_min = -2**23

        physical_max = 4.5 / gain
        physical_min = -4.5 / gain


        yield pad("Channel " + str(channel), 16)    # Channel label
        yield pad("Passive Electrode", 80)          # Transducer type
        yield pad("uV", 8)                          # Physical Unit
        yield pad(str(physical_min), 8)                     # Physical minimum
        yield pad(str(physical_max), 8)                      # Physical maximum
        yield pad(str(digital_min), 8)    # Digital minimum
        yield pad(str(digital_max), 8)    # Digital maximum
        yield pad("Notch @ 60 Hz", 80)  # Pre-filtering

        yield pad("250", 8)     # Number of samples in each data record

        yield pad("", 32)       # Reserved

import wave

class WAVReader:
  def __init__(self, fileobj):
    self.wave = wave.open(fileobj)

    assert(self.wave.getsampwidth() == 3)
    assert(self.wave.getframerate() == 250)
    assert(self.wave.getnchannels() == 8)

  def readPacket(self):

    channels = [0] * 8
    frame = self.wave.readframes(1)
    for ch in range(8):
        data = frame[ch * 3: ch * 3 + 3]
        data = (b'\xff' if data[0] >> 7 else b'\0') + data
        channels[ch] = struct.unpack('<i', data)[0]

    return channels
