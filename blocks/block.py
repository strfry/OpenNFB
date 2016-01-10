import numpy as np

from gnuradio import gr

class Input(object):
    """Attribute type for describing signal inputs of Blocks"""

    # A counter used to find out the order of declaration 
    order = 0

    def __init__(self, type=np.float32):
        self.order = Input.order
        Input.order += 1

        self.type = type

    """Create a copy from a class attribute for a specific Block instance"""
    def instantiate(self, block, name):
        new = Input(type=self.type)
        new.block = block
        new.name = name
        new.cls = self

        print ('Input.instantiate', self, block, name, new)

        return new


    def __getattr__(self, attrname):
        if 'block' not in self.__dict__:
            raise ValueError('getattr call on uninstantiated Input', self)
        
        if 'source' in self.__dict__:
            return getattr(self.source, attrname)

        raise AttributeError(self, 'Input \'%s\' of Block %s does not have attribute \'%s\', nor any sources'
            % (name, block, attrname))


class Output(object):
    """Attribute type for describing signal outputs of Blocks"""

    # A counter used to find out the order of declaration 
    order = 0

    def __init__(self, source=None, type=np.float32):
        print ('Output init', source, type)
        self.order = Input.order
        Output.order += 1

        self.source = source
        self.type = type

    """Create a copy from a class attribute for a specific Block instance"""
    def instantiate(self, block, name):
        print ('Output.instantiate', self, block, name)
        new = Output(type=self.type)
        new.block = block
        new.name = name

        # Get the instance of the source object
        new.source = block._get_input_instance(self.source)


        return new

    def __getattr__(self, attrname):
        #print ('Output getattr', attrname, self.__dict__['block'])
        #if hasattr(self, attrname):
        #if object(self, attrname):
        #    print ('p3')
        #    return super(self).__getattr__(attrname)

        if hasattr(self.block, attrname):
            return getattr(self.block, attrname)

        source = self.__dict__['source']
        if source:
            return getattr(source, attrname)
        print ('p5')

        raise AttributeError('Output does not have attribute \'' + attrname +
            '\', nor any sources')

class Block(object):
    def _get_input_instance(self, input):
        if not input: return None

        for attr in dir(self):
            inp = getattr(self, attr)
            if type(inp) == Input and inp.cls == input:
                return inp

        raise AttributeError('Can not find %s in %s', (input, self))

    def __init__(self, *args, **kwargs):
        inputs = []
        outputs = []

        # Search block for inputs/outputs, add them to a list
        # Also replace the declaration with a copy (instance)
        for attrname in dir(self):
            attr = getattr(self, attrname)
            if type(attr) in (Input, Output):
                print self, 'found type ', attr, attrname
                #attr = copy.copy(attr)
                attr = attr.instantiate(self, attrname)
                print attr.name, attr.block
                setattr(self, attrname, attr)

                if type(attr) == Input:
                    inputs.append(attr)
                elif type(attr) == Output:
                    outputs.append(attr)
            
        inputs.sort(key=lambda x: x.order)
        outputs.sort(key=lambda x: x.order)

        for i in inputs:
            print ('Block', self, ' Input', i)

        for i in outputs:
            print ('Block', self, ' Output', i)

        print (self, len(args), len(inputs), inputs)
        if len(args) < len(inputs):
            raise ValueError('Not enough arguments for input')

        args = list(args)
        for i, input in enumerate(inputs):
            input.index = i
            source = args.pop(0)

            if isinstance(source, Block):
                source = source.output
                print ('Assign output', self, source)

            input.source = source

        for i, output in enumerate(outputs):
            output.index = i

        input_types = [x.type for x in inputs]
        output_types = [x.type for x in outputs]

        name = self.__class__.__name__

        if hasattr(self, 'general_work'):
            self.gr_block = gr.basic_block(name, input_types, output_types)
            self.gr_block.general_work = self.general_work

        self.init(*args, **kwargs)

        assert hasattr(self, 'gr_block')

class InOutBlock(Block):
    "A base class for the default case of a block with input and one output"
    input = Input()
    output = Output(input)



def wireup(top_block, destination, visited=[]):
    print 'wireup', destination, visited
    if destination in visited: return visited

    visited = visited + [destination]

    for idx in dir(destination):
        inp = getattr(destination, idx)
        if type(inp) == Input:
            top_block.connect(inp.source.block.gr_block, (inp.block.gr_block, inp.index))
            visited += wireup(top_block, inp.source.block, visited)

    return visited

