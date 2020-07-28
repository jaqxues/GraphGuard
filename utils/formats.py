import unittest

from androguard.core.bytecode import FormatClassToJava

# https://source.android.com/devices/tech/dalvik/dex-format#typedescriptor
type_descriptors = {
    "void": "V",
    "boolean": "Z",
    "byte": "B",
    "short": "S",
    "char": "C",
    "int": "I",
    "long": "J",
    "float": "F",
    "double": "D"
}

type_ds_reversed = {v: k for k, v in type_descriptors.items()}


def get_as_type_descriptor(arg):
    if arg.endswith("[]"):
        return "[" + get_as_type_descriptor(arg[:-2])
    if arg in type_descriptors:
        return type_descriptors[arg]
    return FormatClassToJava(arg)


def strip_return_descriptor(descriptor):
    return descriptor[1:descriptor.index(")")]


def pretty_format_class(class_name):
    if class_name.startswith("["):
        return pretty_format_class(class_name[1:]) + "[]"
    if class_name in type_ds_reversed:
        return type_ds_reversed[class_name]
    return class_name[1:-1].replace("/", ".")


def get_pretty_params(descriptor):
    sr = strip_return_descriptor(descriptor)
    if sr:
        return map(pretty_format_class, sr.split(" "))
    return []


def get_method_repr(class_name, method_name, param_types):
    return f"{class_name}#{method_name}({param_types})"


def pretty_format_ma(ma):
    return get_method_repr(pretty_format_class(ma.class_name), ma.name,
                           ", ".join(get_pretty_params(str(ma.descriptor))))


def pretty_format_fa(fa):
    return fa.class_name + "#" + fa.name


def get_usable_description(ma):
    stripped, r = str(ma.descriptor[1:]).split(")")
    return "(" + (" ".join(map(get_usable, stripped.split(" "))) if stripped else "") + ")" + get_usable(r)


def get_usable(class_name):
    if class_name.startswith("["):
        return "[" + get_usable(class_name[1:])

    if class_name.startswith("Ljava/") or class_name.startswith("Landroid/") or class_name in type_descriptors.values():
        return class_name
    return "obfuscated.class"


tests_1 = (
    ("java.lang.String", "Ljava/lang/String;"),
    ("java.lang.String[]", "[Ljava/lang/String;"),
    ("void", "V"),
    ("int[]", "[I"),
    ("char", "C"),
    ("java.lang.Object[][]", "[[Ljava/lang/Object;"),
    ("ABC", "LABC;")
)

tests_2 = (
    ("(I)I", "I"),
    ("(C)Z", "C"),
    ("(Ljava/lang/CharSequence; I)I", "Ljava/lang/CharSequence; I")
)


class TestFunction(unittest.TestCase):
    def test_type_descriptor(self):
        for test, val in tests_1:
            self.assertEqual(get_as_type_descriptor(test), val)

    def test_strip_return(self):
        for test, val in tests_2:
            self.assertEqual(strip_return_descriptor(test), val)

    def test_pretty_class(self):
        for val, test in tests_1:
            self.assertEqual(pretty_format_class(test), val)


if __name__ == "__main__":
    # Run Unittests
    unittest.main(argv=[''], verbosity=2, exit=False)
