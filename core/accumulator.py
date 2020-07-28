from utils.formats import FormatClassToJava, pretty_format_ma


class Accumulator:
    def __init__(self):
        self.candidates_cs = {}
        self.candidates_ms = {}
        self.matching_cs = {}
        self.matching_ms = {}

    def add_candidates(self, candidates_cs=None, candidates_ms=None, candidates_fs=None):
        previous_cs = len(self.matching_cs)
        previous_ms = len(self.matching_ms)

        if candidates_cs is not None:
            for c_name, c_set in candidates_cs.items():

                if len(c_set) == 1:
                    el = list(c_set)[0]
                    print("+ Found single candidate for core Class. Considering it a match!",
                          f"\n\t{c_name} -> {el}")
                    self.matching_cs[c_name] = el
                    continue

                print("* Found multiple candidates for core Class", c_name)

                if c_name in self.candidates_cs:
                    previous = self.candidates_cs[c_name]
                    combined = previous & c_set

                    if len(combined) == 0:
                        print("- Inner join on possible candidates resulted in no match for Class", c_name)
                    elif len(combined) == 1:
                        el = list(combined)[0]
                        print("+ Inner join resulted in single core candidate. Considering it a match!",
                              f"\n\t{c_name} -> {el}")
                        self.matching_cs[c_name] = el

                    elif len(combined) < len(previous):
                        print(".. Inner join narrowed down search.",
                              f"(({len(c_set)} | {len(previous)}) -> {len(combined)})")

                    self.candidates_cs[c_name] = combined
                else:
                    self.candidates_cs[c_name] = c_set

        if candidates_ms is not None:
            for m_dec, m_set in candidates_ms.items():

                if len(m_set) == 1:
                    el = list(m_set)[0]
                    print("+ Found single candidate for core Method. Considering it a match",
                          f"\n\t{m_dec.pretty_format()} -> {pretty_format_ma(el)}")
                    self.matching_ms[m_dec] = el
                    continue

                print("* Found multiple candidates for core Method", m_dec.pretty_format())

                if m_dec in self.candidates_ms:
                    previous = self.candidates_ms[m_dec]
                    combined = previous & m_set

                    if len(combined) == 0:
                        print("- Inner join on possible candidates resulted in no match for Method",
                              m_dec.pretty_format())
                    elif len(combined) == 1:
                        el = list(combined)[0]
                        print("+ Inner join resulted in single core candidate. Considering it a match!",
                              f"\n\t{m_dec.pretty_format()} -> {pretty_format_ma(el)}")
                        self.matching_ms[m_dec] = el
                    elif len(combined) < len(previous):
                        print(".. Inner join narrowed down search.",
                              f"(({len(m_set) | len(previous)}) -> {len(combined)})")

                    self.candidates_ms[m_dec] = combined
                else:
                    self.candidates_ms[m_dec] = m_set

        # Clear Candidates after match was found
        for m_dec in self.matching_ms.keys():
            if m_dec in self.candidates_ms:
                del self.candidates_ms[m_dec]

            if FormatClassToJava(m_dec.class_name) not in self.matching_cs:
                c_name = FormatClassToJava(m_dec.class_name)
                c_name2 = self.matching_ms[m_dec].class_name
                self.matching_cs[c_name] = c_name2
                print("+ Matching Class of single candidate method match",
                      f"\n\t{c_name} -> {c_name2}")

        for c_name in self.matching_cs.keys():
            if c_name in self.candidates_cs:
                del self.candidates_cs[c_name]

        print(
            f"Could resolve {len(self.matching_cs) - previous_cs} new Classes, {len(self.matching_ms) - previous_ms} new Methods")

    def get_unmatched_ms(self, m_decs):
        return tuple(filter(lambda x: x not in self.matching_ms, m_decs))

    def get_unmatched_cs(self, c_decs):
        return set(map(FormatClassToJava, c_decs)) - set(self.matching_cs.keys())

    def get_unmatched_fs(self, f_decs):
        return tuple()
