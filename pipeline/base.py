import abc

# Ports

class DataPort(object):
    def __init__(self, component):
        self.component = component
        self.connection = None
        self._buffer = None

    def connect(self, port):
        self.connection = port
        port.conncetion = self

class _InputPort(DataPort):
    @property
    def value(self):
        return self._buffer

    @value.setter
    def value(self, value):
        self._buffer = value

class _OutputPort(DataPort):
    @property
    def value(self):
        return self._buffer

    @value.setter
    def value(self, value):
        self._buffer = value
        if self.connection is not None:
            self.connection.value = value

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

class ComponentMeta(abc.ABCMeta):
    def __init__(cls, name, bases, attributes):
        super(ComponentMeta, cls).__init__(name, bases, attributes)
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
        self.input_ports = []
        self.output_ports = []
        for attr_name, attr in self.__inputs__.items():
            port = attr(self)
            setattr(self, attr_name, port)
            self.input_ports.append(port)
        for attr_name, attr in self.__outputs__.items():
            port = attr(self)
            setattr(self, attr_name, port)
            self.output_ports.append(port)

    @abc.abstractmethod
    def process(self):
        if any(port.value is None for port in self.input_ports):
            raise ValueError("Not all input ports' buffers are populated in {}.".format(self))

    def process_all(self):
        """naive/temporary way to process all components. can cause infinite recursion"""
        self.process()
        for port in self.output_ports:
            if port.connection is not None:
                port.connection.component.process_all()