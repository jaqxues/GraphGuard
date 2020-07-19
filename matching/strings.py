from collections import defaultdict, Counter
from androguard.core.bytecode import FormatClassToJava

from matching.matcher import Matcher

MAX_USAGE_COUNT_STR = 20


class StringMatcher(Matcher):
    def __init__(self, *args):
        super().__init__(*args)

    def get_counters(self):
        c_strs, m_strs = defaultdict(list), defaultdict(list)

        for s, xrefs in get_filtered_strs(self.dx):
            for x in xrefs:
                c_ref, m_ref = x

                if c_ref.name not in self.resolved_classes:
                    # XReference not in a Class or method that we need to find
                    continue

                # Loop through each method and find methods in this class
                for m_dec in self.m_decs:
                    r_m = self.decs_ma[m_dec]
                    if r_m.class_name != c_ref.name:
                        continue

                    # String is used in a class we need to find
                    c_strs[c_ref.name].append(s.value)

                    if m_ref == r_m:
                        # String is used in this method
                        m_strs[m_dec].append(s.value)

        c_strs = {k: Counter(v) for k, v in c_strs.items()}
        m_strs = {k: Counter(v) for k, v in m_strs.items()}
        return c_strs, m_strs

    def get_counters2(self, c_strs, m_strs):
        c_strs2, m_strs2 = defaultdict(list), defaultdict(list)

        to_find = set().union(*map(lambda x: set(x.keys()), c_strs.values()),
                              *map(lambda x: set(x.keys()), m_strs.values()))

        for s in self.dx2.get_strings():
            if s.value not in to_find:
                continue

            for m_dec, m_counter in m_strs.items():
                c_name = FormatClassToJava(m_dec.class_name)

                c_counter = c_strs[c_name] if c_name in c_strs else Counter()

                if s.value in m_counter:
                    for x in get_xrefs_if_usable(s):
                        m_strs2[x[1]].append(s.value)
                if s.value in c_counter:
                    for x in get_xrefs_if_usable(s):
                        c_strs2[str(x[0].name)].append(s.value)

        c_strs2 = {k: Counter(v) for k, v in c_strs2.items()}
        m_strs2 = {k: Counter(v) for k, v in m_strs2.items()}

        return c_strs2, m_strs2

    def compare_counters(self):
        c_strs, m_strs, = self.get_counters()
        c_strs2, m_strs2 = self.get_counters2(c_strs, m_strs)

        candidates_cs, candidates_ms = defaultdict(set), defaultdict(set)

        def compare(dict2, dict1, to_dic):
            for k2, c2 in dict2.items():
                for k1, c1 in dict1.items():
                    if c1 == c2:
                        to_dic[k1].add(k2)

        compare(c_strs2, c_strs, candidates_cs)
        compare(m_strs2, m_strs, candidates_ms)

        return candidates_cs, candidates_ms


def get_filtered_strs(dx, max_usage_count=MAX_USAGE_COUNT_STR):
    """
    Loops through all strings that are referenced less than MAX_USAGE_COUNT_STR times and hence can be
    used as characteristic for finding methods or classes.
    """
    return ((s, xrefs)
            for s, xrefs in map(lambda s: (s, s.get_xref_from()), dx.get_strings())
            if len(xrefs) <= max_usage_count)


def get_xrefs_if_usable(s, max_usage_count=MAX_USAGE_COUNT_STR):
    """
    Loops through xrefs of a string only if the number of references does not exceed MAX_USAGE_COUNT_STR.
    """
    xrefs = s.get_xref_from()
    if len(xrefs) > max_usage_count:
        return
    yield from xrefs
