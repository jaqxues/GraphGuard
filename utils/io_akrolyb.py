import logging
import re
from collections.abc import Iterable

from utils.formats import pretty_format_class, get_pretty_params
from utils.utils import safe_replace, AmbiguousStringReplacement

from androguard.core.bytecode import FormatClassToJava

m_dec_regex = re.compile(
    r"val ([A-Za-z0-9_]+) = (/\* TODO \*/ )?(MethodDec|ConstructorDec)\(\s*([A-Za-z0-9_]+),\s*(\"([A-Za-z0-9_]+)\")?,*\s*(.+)\s*([^)]*)\)",
    # r"val ([A-Za-z0-9_]+) = (/\* TODO \*/ )?(MethodDec|ConstructorDec)\(\s*([A-Za-z0-9_]+),\s*(\"([A-Za-z0-9_]+)\")?,*\s*(.+)\s*(.*)\s*\)",
    re.MULTILINE
)
f_dec_regex = re.compile(
    r"@FieldClass\((.*)\)\s*.*val ([A-Za-z0-9_$]+) = (/\* TODO \*/ )?VariableDec<(.*)>\(\"([A-Za-z0-9._$]+)\"\)")
logging.basicConfig(format='%(message)s')


def replace_cs(c_txt, accumulator):
    # Mark All items with /* _TODO_ */ Comments
    c_txt = c_txt.replace("ClassDec(", "/* TODO */ ClassDec(")

    for c1, c2 in accumulator.matching_cs.items():
        c1, c2 = pretty_format_class(c1), pretty_format_class(c2)
        c_txt = c_txt.replace(f'/* TODO */ ClassDec("{c1}")', f'ClassDec("{c2}")')

    return c_txt


def replace_ms(m_txt, accumulator, named_m_decs):
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

        # Try Replacing Automatically. If ambiguous replacement, mark with _TODO_ Comment + Appropriate Message
        try:
            dec_txt = m.group(0)

            # Remove /* _TODO_ */ Comments
            dec_txt = dec_txt.replace(m.group(2), "")

            # Replace Method Name
            assert ((m.group(6) is None) and (m_dec.name == "<init>")) or (m.group(6) == m_dec.name), \
                "Broke Constructor/Method Integrity"
            if m.group(6):
                dec_txt = safe_replace(dec_txt, m.group(5), f'"{str(m2.name)}"')

            # Parameters
            if m.group(8) and not m_dec.skip_params:
                params = m.group(8)
                for p1, p2 in zip(get_pretty_params(str(m1.descriptor)), get_pretty_params(str(m2.descriptor))):
                    params = params.replace(f'"{p1}"', f'"{p2}"')
                dec_txt = safe_replace(dec_txt, m.group(8), params)
        except AmbiguousStringReplacement as e:
            logging.warning(e)
            dec_txt = m.group(0).replace(m.group(3), "/* TODO: Ambiguous String Replacement */ ")
        m_txt = m_txt.replace(m.group(0), dec_txt)

    return m_txt


def replace_fs(f_txt, accumulator, named_f_decs):
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
                if FormatClassToJava(f_dec.class_name) in accumulator.matching_cs:
                    cl2 = pretty_format_class(accumulator.matching_cs[FormatClassToJava(f_dec.class_name)])
                    cls[f'"{f_dec.class_name}"'] = f'"{cl2}"'
                    print("Only updating matched Class:", f_dec.class_name, "->", cl2)
                    f1 = None
                else:
                    cls[f'"{f_dec.class_name}"'] = f'/* TODO */ "{f_dec.class_name}"'
                    continue
            if f1:
                f2 = accumulator.matching_fs[f1]
                f2_names.add(f2.name)
                cls[f'"{f_dec.class_name}"'] = f'"{pretty_format_class(str(f2.get_class_name()))}"'
        if not (f2_names or cls):
            continue

        assert len(f2_names) <= 1, f"Field of multiple class no longer have the same name {f2_names}"

        # Try Replacing Automatically. If ambiguous replacement, mark with _TODO_ Comment + Appropriate Message
        try:
            dec_txt = m.group(0)

            # Change Classes
            c_group = m.group(1)
            for c1, c2 in cls.items():
                c_group = safe_replace(c_group, c1, c2)
            dec_txt = safe_replace(dec_txt, m.group(1), c_group)

            if f2_names:
                # Remove /* _TODO_ */ Comment
                if m.group(3):
                    dec_txt = safe_replace(dec_txt, m.group(3), "")

                # Replace Field Name
                dec_txt = safe_replace(dec_txt, f'"{m.group(5)}"', f'"{str(list(f2_names)[0])}"')
        except AmbiguousStringReplacement as e:
            logging.warning(e)
            dec_txt = m.group(0).replace(m.group(3), "/* TODO: Ambiguous String Replacement */ ")

        f_txt = safe_replace(f_txt, m.group(0), dec_txt)
    return f_txt


def _read_file(x_f):
    with open(x_f, 'r') as f:
        return f.read()


def replace_cs_f(c_file, accumulator):
    return replace_cs(_read_file(c_file), accumulator)


def replace_ms_f(m_file, accumulator, named_m_decs):
    return replace_ms(_read_file(m_file), accumulator, named_m_decs)


def replace_fs_f(f_file, accumulator, named_f_decs):
    return replace_fs(_read_file(f_file), accumulator, named_f_decs)
