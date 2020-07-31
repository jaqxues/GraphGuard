from collections import defaultdict, Counter

from strategies.strategy import Strategy

MAX_USAGE_COUNT_STR = 20
UNIQUE_STRINGS_MAJORITY = 2 / 3


class StringStrategy(Strategy):
    def get_counters(self):
        c_strs, m_strs = defaultdict(list), defaultdict(list)

        r_cas_set = set(self.r_cas)
        r_mas_set = set(self.r_mas)
        for s, xrefs in get_filtered_strs(self.dx):
            for x in xrefs:
                c_ref, m_ref = x

                if c_ref.name in r_cas_set:
                    c_strs[c_ref.name].append(s.value)

                # Loop through each method and find methods in this class
                if m_ref in r_mas_set:
                    m_strs[m_ref].append(s.value)

        c_strs = {str(k): Counter(v) for k, v in c_strs.items()}
        m_strs = {k: Counter(v) for k, v in m_strs.items()}
        return c_strs, m_strs

    def get_counters2(self, c_strs, m_strs):
        c_strs2, m_strs2 = defaultdict(list), defaultdict(list)

        to_find = set().union(*map(lambda v: set(v.keys()), c_strs.values()),
                              *map(lambda v: set(v.keys()), m_strs.values()))

        for s in self.dx2.get_strings():
            if s.value not in to_find:
                continue

            for c_name in self.r_cas:
                c_counter = c_strs[c_name] if c_name in c_strs else Counter()
                if s.value in c_counter:
                    for x in get_xrefs_if_usable(s):
                        c_strs2[str(x[0].name)].append(s.value)

            for ma in self.r_mas:
                m_counter = m_strs[ma] if ma in m_strs else Counter()

                if s.value in m_counter:
                    for x in get_xrefs_if_usable(s):
                        m_strs2[x[1]].append(s.value)

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

    def compare_unique_strings(self):
        unique_strs = defaultdict(set)
        c_names = {str(ca.name) for ca in self.r_cas}

        for s, xrefs in get_filtered_strs(self.dx):
            cn = list(xrefs)[0][0].name
            if used_only_in_class(xrefs, cn):
                if cn in c_names:
                    unique_strs[cn].add(s.value)

        all_strs = set().union(*unique_strs.values())

        unique_strs2 = defaultdict(set)
        for s, xrefs in get_filtered_strs(self.dx2):
            if s.value in all_strs:
                cn = list(xrefs)[0][0].name
                if used_only_in_class(xrefs, cn):
                    unique_strs2[cn].add(s.value)
                else:
                    print(f"~ Unique String not used in single class anymore. Change! ({s.value})")
                    pass

        tmp_candidates_cs = defaultdict(list)
        for c1, strset1 in unique_strs.items():
            for s1 in strset1:
                for c2, strset2 in unique_strs2.items():
                    if s1 not in strset2:
                        continue
                    tmp_candidates_cs[str(c1)].append(str(c2))

        tmp_candidates_cs = {k: Counter(v) for k, v in tmp_candidates_cs.items()}

        candidates = {}
        for c, counter in tmp_candidates_cs.items():
            if len(counter) == 1:
                c_name, count = tuple(*counter.items())
                candidates[c] = c_name
                continue

            total = sum(counter.values())
            for c2, count in counter.items():
                if count / total >= UNIQUE_STRINGS_MAJORITY:
                    print(".. Considering ambiguous match by UniqueString as match with a majority of",
                          f"{(count / total):.2f} ({c} -> {c2})")
                    candidates[c] = c2
                    break

        return {k: {v} for k, v in candidates.items()}


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


def used_only_in_class(xrefs, c_name):
    # if string only used in one class, regardless of the number of references
    return all((xref[0].name == c_name for xref in xrefs))
