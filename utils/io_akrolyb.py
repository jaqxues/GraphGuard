import re
from collections.abc import Iterable

from utils.formats import pretty_format_class, get_pretty_params

m_dec_regex = re.compile(
    r"val ([A-Za-z0-9_]+) = (/\* TODO \*/ )?(MethodDec|ConstructorDec)\(\s*([A-Za-z0-9_]+),\s*(\"([A-Za-z0-9_]+)\")?,*\s*(.+)\s*(.*)\)",
    # r"val ([A-Za-z0-9_]+) = (/\* TODO \*/ )?(MethodDec|ConstructorDec)\(\s*([A-Za-z0-9_]+),\s*(\"([A-Za-z0-9_]+)\")?,*\s*(.+)\s*(.*)\s*\)",
    re.MULTILINE
)
f_dec_regex = re.compile(
    r"@FieldClass\((.*)\)\s*.*val ([A-Za-z0-9_$]+) = (/\* TODO \*/ )?VariableDec<(.*)>\(\"([A-Za-z0-9._$]+)\"\)")


def replace_cs(c_file, accumulator):
    with open(c_file, "r") as f:
        c_txt = f.read()

    # Mark All items with /* _TODO_ */ Comments
    c_txt = c_txt.replace("ClassDec(", "/* TODO */ ClassDec(")

    for c1, c2 in accumulator.matching_cs.items():
        c1, c2 = pretty_format_class(c1), pretty_format_class(c2)
        c_txt = c_txt.replace(f'/* TODO */ ClassDec("{c1}")', f'ClassDec("{c2}")')

    return c_txt


def replace_ms(m_file, accumulator, named_m_decs):
    with open(m_file, "r") as f:
        m_txt = f.read()

    # Mark All items with /* _TODO_ */ Comments
    m_txt = re.sub(r"((MethodDec|ConstructorDec)\()", r"/* TODO */ \1", m_txt)

    for m in m_dec_regex.finditer(m_txt):
        name = m.group(1)

        if name not in named_m_decs:
            print("MethodDec", name, "not registered")
            continue

        m_dec = named_m_decs[name]
        for m1 in accumulator.matching_ms:
            if m_dec.equals_ma(m1):
                break
        else:
            print("No matching Method found for", m_dec.pretty_format())
            continue

        m2 = accumulator.matching_ms[m1]

        dec_txt = m.group(0)

        # Remove /* _TODO_ */ Comments
        dec_txt = dec_txt.replace(m.group(2), "")

        # Replace Method Name
        assert ((m.group(6) is None) and (m_dec.name == "<init>")) or (m.group(6) == m_dec.name)
        if m.group(6):
            assert dec_txt.count(m.group(5)) == 1, "Ambiguous String Replacement"
            dec_txt = dec_txt.replace(m.group(5), f'"{str(m2.name)}"')

        # Parameters
        if m.group(8) and not m_dec.skip_params:
            params = m.group(8)
            for p1, p2 in zip(get_pretty_params(str(m1.descriptor)), get_pretty_params(str(m2.descriptor))):
                params = params.replace(f'"{p1}"', f'"{p2}"')
            assert dec_txt.count(m.group(8)) == 1, "Ambiguous String Replacement"
            dec_txt = dec_txt.replace(m.group(8), params)

        m_txt = m_txt.replace(m.group(0), dec_txt)

    return m_txt


def replace_fs(f_file, accumulator, named_f_decs):
    with open(f_file, "r") as f:
        f_txt = f.read()

    f_txt = f_txt.replace("VariableDec<", "/* TODO */ VariableDec<")

    for m in f_dec_regex.finditer(f_txt):
        name = m.group(2)

        if name not in named_f_decs:
            print("FieldDec", name, "not registered")
            continue

        f_decs = named_f_decs[name]
        if not isinstance(f_decs, Iterable):
            f_decs = (f_decs,)

        f_name = f_decs[0].name
        for f_dec in f_decs:
            assert f_name == f_dec.name

        cls = {}
        f2_names = set()

        for f_dec in f_decs:
            for f1 in accumulator.matching_fs:
                if f_dec.class_name == pretty_format_class(str(f1.get_class_name())) and f_dec.name == str(f1.name):
                    break
            else:
                print("No matching Field found for", f_dec.pretty_format())
                cls[f'"{f_dec.class_name}"'] = f'/* TODO */ "{f_dec.class_name}"'
                continue
            f2 = accumulator.matching_fs[f1]
            f2_names.add(f2.name)
            cls[f'"{f_dec.class_name}"'] = f'"{pretty_format_class(str(f2.get_class_name()))}"'
        if not f2_names:
            continue

        assert len(f2_names) == 1, f"Field of multiple class no longer have the same name {f2_names}"

        dec_txt = m.group(0)

        # Remove /* _TODO_ */ Comment
        if m.group(3):
            dec_txt = dec_txt.replace(m.group(3), "")

        # Change Classes
        c_group = m.group(1)
        for c1, c2 in cls.items():
            assert c_group.count(c1) == 1, "Ambiguous String Replacement"
            c_group = c_group.replace(c1, c2)
        assert dec_txt.count(m.group(1)) == 1, "Ambiguous String Replacement"
        dec_txt = dec_txt.replace(m.group(1), c_group)

        # Replace Field Name
        dec_txt = dec_txt.replace(f'"{m.group(5)}"', f'"{str(list(f2_names)[0])}"')
        assert dec_txt.count(f'"{m.group(5)}"') == 1, "Ambiguous String Replacement"

        assert f_txt.count(m.group(0)) == 1, "Ambiguous String Replacement"
        f_txt = f_txt.replace(m.group(0), dec_txt)
    return f_txt
