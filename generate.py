from formats import pretty_format_class, get_pretty_params


def generate_decs(decs, matching_ms):
    last = len(decs) - 1
    print("decs_to_find = (")
    for idx, m_dec in enumerate(decs):
        if m_dec in matching_ms:
            ma = matching_ms[m_dec]
            print("\tMethodDec('", pretty_format_class(ma.class_name), "', '", ma.name, "'", sep="", end="")
            for p in get_pretty_params(str(ma.get_descriptor())):
                print(", '", p, "'", sep="", end="")
            print(")", end="")
        else:
            print("\t# No match for MethodDec", m_dec.pretty_format(), end="")
        if idx < last:
            print(",")
        else:
            print()
    print(")")
