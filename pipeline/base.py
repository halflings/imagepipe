# Ports

class DataPort(object):
    connection = None
    def __init__(self, component):
        self.component = component

class _InputPort(DataPort):
    pass

class _OutputPort(DataPort):
    def connect(self, port):
        if not isinstance(port, _InputPort):
            raise ValueError("An output port can only be connected to an input port.")
        self.connection = port
        port.conncetion = self

def generate_port_class(parent_cls, port_name, *args, **kwargs):
    class NewClass(parent_cls):
        name = port_name
        def __init__(self, component):
            super(NewClass, self).__init__(component, *args, **kwargs)
    NewClass.__name__ = port_name.title().replace(' ', '')
    return NewClass

def InputPort(name, *args, **kwargs):
    return generate_port_class(_InputPort, name, *args, **kwargs)

def OutputPort(name, *args, **kwargs):
    return generate_port_class(_OutputPort, name, *args, **kwargs)

# Components

class ComponentMeta(type):
    def __init__(cls, name, bases, attributes):
        cls.__inputs__ = dict()
        cls.__outputs__ = dict()
        for attr_name, attr in attributes.iteritems():
            if type(attr) is type:
                if issubclass(attr, _InputPort):
                    cls.__inputs__[attr_name] = attr
                    delattr(cls, attr_name)
                elif issubclass(attr, _OutputPort):
                    cls.__outputs__[attr_name] = attr
                    delattr(cls, attr_name)

    def __str__(self):
        return "< Component '{}': Inputs: {}, Outputs: {} >".format(self.__name__, self.__inputs__.keys(),
                                                                    self.__outputs__.keys())

class Component(object):
    __metaclass__ = ComponentMeta

    def __init__(self, name):
        self.name = name
        # Initializing the ports' instances
        for attr_name, attr in self.__inputs__.items() + self.__outputs__.items():
            if issubclass(attr, DataPort):
                setattr(self, attr_name, attr(self))

    def process(self):
        if not all(p.connection is not None for p in self.input_ports):
            raise ValueError("Not all input ports are connected.")

# Example application
if __name__ == '__main__':

    class BlackWhite(Component):
        colored_image = InputPort("Colored image")
        black_and_white = OutputPort("Black and White image")

    class Resize(Component):
        original_image = InputPort("Original image")
        resized_image = OutputPort("Resized image")

    bw = BlackWhite('bw1')
    resize = Resize('rsz1')
    resize_bis = Resize('rsz2')

    resize.resized_image.connect(bw.colored_image)

    print "BlackWhite components description = {}".format(BlackWhite)
    print ', '.join("{} = {}".format(comp.name, comp) for comp in [bw, resize, resize_bis])
    port = resize.resized_image
    print "{} is connected to {}, of component {}".format(port, port.connection, port.connection.component)