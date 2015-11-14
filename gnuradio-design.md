## Rationale

The previous OpenNFB implementation	


For performance reasons, OpenNFB uses GnuRadio as a processing backend.
The Lua protocol frontend adds a layer of syntactic sugar above GnuRadios python API.

In GnuRadio, blocks and connections are explicitly instantiated, like this:
   source = blocks.udp_source(...)
   filt = filter.iir_filter_ffd(...)
   self.connect((source, 0), (filt, 0))

In OpenNFB, the syntax looks more like this:
   src = udp_source(...)
   filtered = BandPass(src, ...)

The main difference is that explicit calls to connect() are replaced with passing blocks directly to the next block they are processed by.


## Terminology

Blocks - A signal processing element, like a filter, a mathematical operation, or a display element. Often directly translates to a GnuRadio block.
Signal - 
Parameter - A value that might change during execution, but not a real signal with a fixed sample rate.

## Multiple Outputs

GnuRadio supports multiple inputs/outputs of blocks by passing an index with the block on the connect() call.
This means that different outputs do not have names, just an index. The connection between index and name has to be made clear by the block
documentation, and looked up or remembered on every use.

With OpenNFB, most blocks have a default output. This one is used when the whole block is passed to the next block, like in the example above.
Some blocks, like Thresholds, have many different named outputs.

   t = Threshold(src, mode='increase', passrate=0.95)
   vm1 = VMeter(t.ratio)

## Stream tags

GnuRadio provides another metadata mechanism, stream tags.
While messages are asynchronous to the sample flow, which is fine for things like
UI controls, stream tags are strictly associated with a sample.
This enables a kind of block that does not modify the data, but adds additional information.
For example, an artifact detection threshold could mark certain segments as tainted
by artifact, so later processing blocks can stop feedback on these samples.


## UI building

Some blocks are made for displaying signals, like Oscilloscopes or Meters, others can be used as parameter sources, like Sliders.
There are elements like Thresholds, that work as processing blocks, but have an UI component that can be optionally instantiated to interact with.

UI components can be grouped horizontally and vertically to determine the layout

  m1 = VMeter(s1)
  m2 = VMeter(s2)
  return hgroup('Meters', m1, m2)



## OpenNFB Block


class BandPass(Block):
  input = Input()
  output = Output(input)

  def init(self, lo, hi):
    self.input = self.declare_input()
    self.output = self.declare_output(self.input)

    SAMPLERATE = input.sample_rate
    filter_ab = scipy.signal.iirfilter(8, [lo / SAMPLERATE, hi / SAMPLERATE], btype='bandpass')

    self.gr_block = filter.iir_filter_ffd(filter_ab[0], filter_ab[1], oldstyle=False)
    
OpenNFB expects a GnuRadio block in gr_block.
If the class implements the method general_work(), a gr_block will be generated
and assigned this work function.

The inputs and outputs map to the GnuRadio indices by their order of declaration.

class Threshold(Block):
  input = Input()
  passfail = Output(input, type=bool)
  ratio = Output(input)

passfail would index=0, ratio index=1

The first (optional) argument of an Output is the Input it is derived by.
This means that metadata, like color or samplerate are deferred to this signal.

The default type for all signals is double. It can be overriden with the type parameter.

The init() method is called by the native __init__ constructor, which should generally
not be overridden.
The first parameters to __init__ are used to initialize the Input() fields,
the remaining parameters are passed on to init().

