from androguard.core.bytecode import FormatClassToJava

from formats import strip_return_descriptor, get_as_type_descriptor, get_method_repr


class MethodDec:
    def __init__(self, class_name, name, *param_types, skip_params=False):
        self.name = name
        self.class_name = class_name
        self.param_types = param_types
        self.skip_params = skip_params

    def get_formatted_param_types(self):
        return list(map(get_as_type_descriptor, self.param_types))

    def param_types_repr(self):
        if self.skip_params:
            return "skip.params"
        return " ".join(self.get_formatted_param_types())

    def get_formatted_class(self):
        return FormatClassToJava(self.class_name)

    def pretty_format(self):
        return get_method_repr(self.class_name, self.name,
                               ("skip.params" if self.skip_params else ", ".join(self.param_types)))

    def __repr__(self):
        return f'MethodDec({self.pretty_format()})'

    def equals_ma(self, ma):
        return self.name == ma.name and (self.skip_params or
                                         self.param_types_repr() == strip_return_descriptor(str(ma.get_descriptor())))

    def find_ma(self, cas):
        for ma in cas[FormatClassToJava(self.class_name)].get_methods():
            if self.equals_ma(ma):
                return ma
        raise Exception(f"Unresolved MethodDec: {self.pretty_format()}")


def resolve_classes(dx, m_decs):
    # Key:   TypeDescriptor Representation of class
    # Value: Androguard Class Analysis Object
    return {cname: dx.get_class_analysis(cname) for cname in map(lambda dec: FormatClassToJava(dec.class_name), m_decs)}


def resolve_methods(m_decs, cas):
    # List of MethodAnalysis Objects
    return tuple((m.find_ma(cas) for m in m_decs))
