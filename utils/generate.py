from utils.formats import pretty_format_class, get_pretty_params, pretty_format_ma, FormatClassToJava


def generate_m_decs(m_decs, r_mas, matching_ms):
    print("m_decs = (")
    for idx, ma in enumerate(r_mas):
        if ma in matching_ms:
            ma = matching_ms[ma]
            print("    MethodDec('", pretty_format_class(ma.class_name), "', '", ma.name, "'", sep="", end="")
            for p in get_pretty_params(str(ma.get_descriptor())):
                print(", '", p, "'", sep="", end="")
            print("),")
        else:
            print(f"    # No match for Method {pretty_format_ma(ma)},")
    print(")")


def generate_c_decs(c_decs, r_cas, matching_cs):
    print("c_decs = (", end="")
    for c_dec in c_decs:
        print()
        cname = FormatClassToJava(c_dec)
        print(" " * 4, end="")
        if cname in matching_cs:
            cname = matching_cs[cname]
        else:
            print("# No Match Found for Class ", end="")
        print(f"'{pretty_format_class(cname)}'", end="")
    print(",")
    print(")")


def generate_f_decs(f_decs, r_fas, matching_fs):
    print('f_decs = (')
    for f_dec in f_decs:
        for fa in r_fas:
            if FormatClassToJava(f_dec.class_name) == fa.get_field().get_class_name() and f_dec.name == fa.name:
                break
        else:
            raise Exception("Field not resolved")
        print(" " * 4, end="")
        if fa in matching_fs:
            fa = matching_fs[fa]
        else:
            fa = fa.get_field()
            print("# No Match Found for Field ", end="")
        print(f"FieldDec('{pretty_format_class(fa.get_class_name())}', '{fa.get_name()}'),")
    print(")")
