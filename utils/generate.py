from utils.formats import pretty_format_class, get_pretty_params, pretty_format_ma


def generate_decs(r_mas, matching_ms):
    last = len(r_mas) - 1
    print("m_decs = (")
    for idx, ma in enumerate(r_mas):
        if ma in matching_ms:
            ma = matching_ms[ma]
            print("\tMethodDec('", pretty_format_class(ma.class_name), "', '", ma.name, "'", sep="", end="")
            for p in get_pretty_params(str(ma.get_descriptor())):
                print(", '", p, "'", sep="", end="")
            print(")", end="")
        else:
            print("\t# No match for Method", pretty_format_ma(ma), end="")
        if idx < last:
            print(",")
        else:
            print()
    print(")")
