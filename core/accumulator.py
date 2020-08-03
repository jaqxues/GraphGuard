from utils.formats import pretty_format_ma, pretty_format_fa


class Accumulator:
    def __init__(self):
        self.candidates_cs = {}
        self.candidates_ms = {}
        self.candidates_fs = {}
        self.matching_cs = {}
        self.matching_ms = {}
        self.matching_fs = {}

    def add_candidates(self, candidates_cs=None, candidates_ms=None, candidates_fs=None):
        previous_cs = len(self.matching_cs)
        previous_ms = len(self.matching_ms)
        previous_fs = len(self.matching_fs)

        if candidates_cs is not None:
            for c_name, c_set in candidates_cs.items():

                if len(c_set) == 1:
                    el = list(c_set)[0]
                    print("+ Found single candidate for Class. Considering it a match!",
                          f"\n\t{c_name} -> {el}")
                    self.matching_cs[c_name] = el
                    continue

                print("* Found multiple candidates for Class", c_name)

                if c_name in self.candidates_cs:
                    previous = self.candidates_cs[c_name]
                    combined = previous & c_set

                    if len(combined) == 0:
                        print("- Inner join on possible candidates resulted in no match for Class", c_name)
                    elif len(combined) == 1:
                        el = list(combined)[0]
                        print("+ Inner join resulted in single candidate for Class. Considering it a match!",
                              f"\n\t{c_name} -> {el}")
                        self.matching_cs[c_name] = el

                    elif len(combined) < len(previous):
                        print(".. Inner join narrowed down search.",
                              f"(({len(c_set)} | {len(previous)}) -> {len(combined)})")

                    self.candidates_cs[c_name] = combined
                else:
                    self.candidates_cs[c_name] = c_set

        if candidates_ms is not None:
            for ma, m_set in candidates_ms.items():

                if len(m_set) == 1:
                    el = list(m_set)[0]
                    print("+ Found single candidate for Method. Considering it a match",
                          f"\n\t{pretty_format_ma(ma)} -> {pretty_format_ma(el)}")
                    self.matching_ms[ma] = el
                    continue

                print("* Found multiple candidates for Method", pretty_format_ma(ma))

                if ma in self.candidates_ms:
                    previous = self.candidates_ms[ma]
                    combined = previous & m_set

                    if len(combined) == 0:
                        print("- Inner join on possible candidates resulted in no match for Method",
                              pretty_format_ma(ma))
                    elif len(combined) == 1:
                        el = list(combined)[0]
                        print("+ Inner join resulted in single candidate for Method. Considering it a match!",
                              f"\n\t{pretty_format_ma(ma)} -> {pretty_format_ma(el)}")
                        self.matching_ms[ma] = el
                    elif len(combined) < len(previous):
                        print(".. Inner join narrowed down search.",
                              f"(({len(m_set)} | {len(previous)}) -> {len(combined)})")

                    self.candidates_ms[ma] = combined
                else:
                    self.candidates_ms[ma] = m_set

        if candidates_fs is not None:
            for fa, f_set in candidates_fs.items():
                if len(f_set) == 1:
                    el = list(f_set)[0].get_field()
                    print("+ Found single candidate for Field. Considering it a match",
                          f"\n\t{pretty_format_fa(fa.get_field())} -> {pretty_format_fa(el)}")
                    self.matching_fs[fa] = el
                    continue

                print("* Found multiple candidates for Field", pretty_format_fa(fa.get_field()))

                if fa in self.candidates_fs:
                    previous = self.candidates_fs[fa]
                    combined = previous & f_set

                    if len(combined) == 0:
                        print("- Inner join on possible candidates resulted in no match for Field",
                              pretty_format_fa(fa.get_field()))
                    elif len(combined) == 1:
                        el = list(combined)[0]
                        print("+ Inner join resulted in single candidate for Field. Considering it a match!",
                              f"\n\t{pretty_format_fa(fa.get_field())} -> {pretty_format_fa(el)}")
                        self.matching_fs[fa] = el
                    elif len(combined) < len(previous):
                        print(".. Inner join narrowed down search",
                              f"(({len(f_set)} | {len(previous)}) -> {len(combined)})")

                    self.candidates_fs[fa] = combined
                else:
                    self.candidates_fs[fa] = f_set

        # Clear Candidates after match was found
        for ma in self.matching_ms:
            if ma in self.candidates_ms:
                del self.candidates_ms[ma]

            if str(ma.class_name) not in self.matching_cs:
                c_name = str(ma.class_name)
                c_name2 = str(self.matching_ms[ma].class_name)
                self.matching_cs[c_name] = c_name2
                print("+ Matching Class of single candidate method match",
                      f"\n\t{c_name} -> {c_name2}")

        for fa in self.matching_fs.keys():
            if fa in self.candidates_fs:
                del self.candidates_fs[fa]

        for c_name in self.matching_cs.keys():
            if c_name in self.candidates_cs:
                del self.candidates_cs[c_name]

        print(f"Could resolve {len(self.matching_cs) - previous_cs} new Classes, "
              f"{len(self.matching_ms) - previous_ms} new Methods, "
              f"{len(self.matching_fs) - previous_fs} new Fields.")

    def get_unmatched_ms(self, r_mas):
        return tuple(filter(lambda x: x not in self.matching_ms, r_mas))

    def get_unmatched_cs(self, r_cas):
        return tuple((ca for ca in r_cas if ca.name not in self.matching_cs))

    def get_unmatched_fs(self, r_fas):
        return tuple(filter(lambda x: x not in self.matching_fs, r_fas))
