from strategies.strategy import Strategy
from utils.formats import get_usable, pretty_format_fa
from androguard.core.bytecodes.dvm import ClassDefItem

cfs = (
    (lambda f: f.get_access_flags_string(), 4),
    (lambda f: f.get_size(), 5),
)


class FieldStrategy(Strategy):

    def get_types_to_match(self):
        for fa in self.r_fas:
            f_type = str(fa.get_descriptor()).replace("[", "")
            if get_usable(f_type) == "obfuscated.class":
                yield self.dx.get_class_analysis(f_type)

    def try_resolve_fs(self):
        candidates_fs = {}
        for fa in self.r_fas:

            if get_usable(str(fa.get_class_name())) == "obfuscated.class" \
                    and fa.get_class_name() not in self.accumulator.matching_cs:
                print("Class of field", pretty_format_fa(fa), "not matched.")
                continue

            ca = self.dx.get_class_analysis(fa.get_class_name()).get_class()
            ca2 = self.dx2.get_class_analysis(self.accumulator.matching_cs[ca.name]).get_class()

            assert type(ca) == ClassDefItem and type(ca2) == ClassDefItem, \
                f"Tried to match field of external class ({pretty_format_fa(fa)})"

            f2s = tuple(ca2.get_fields())

            # Filtering by Type
            arr, f2_type = self.get_usable_f2_type(str(fa.get_descriptor()))
            if f2_type is not None:
                desc2 = arr + f2_type
                f2s = tuple((fa2 for fa2 in f2s if fa2.get_descriptor() == desc2))

            if not f2s:
                continue

            # Filtering by Score and Compare Functions
            scores = {fa2: sum(((cf(fa) == cf(fa2)) * score) for cf, score in cfs) for fa2 in f2s}
            m = max(scores.values())
            f2s = tuple((fa2 for fa2, score in scores.items() if score == m))

            if tuple((get_usable(str(f.get_descriptor())) for f in ca.get_fields())) == \
                    tuple((get_usable(str(f2.get_descriptor())) for f2 in ca2.get_fields())):
                fa2 = list(ca2.get_fields())[list(ca.get_fields()).index(fa)]
                if fa2 in f2s:
                    f2s = (fa2,)
                else:
                    print(".. Tried to use index, but not in filtered fields!")

            candidates_fs[fa] = set(f2s)

        return candidates_fs

    def get_usable_f2_type(self, desc):
        *arr, c_name = desc.rpartition("[")
        arr = arr[0] + arr[1]

        if get_usable(c_name) == "obfuscated.class":
            if c_name in self.accumulator.matching_cs:
                f2_type = self.accumulator.matching_cs[c_name]
            else:
                f2_type = None
        else:
            f2_type = desc
        return arr, f2_type
