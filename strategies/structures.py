from collections import Counter, defaultdict

from androguard.core.analysis.analysis import FieldAnalysis, ClassAnalysis

from utils.formats import get_usable, get_usable_description
from strategies.strategy import Strategy


class StructureStrategy(Strategy):
    def get_exact_structure_matches(self):
        candidates = defaultdict(set)
        criteria = [
            ClassAnalysis.get_nb_methods,
            lambda ca: len(list(filter(lambda x: x.get_field().get_class_name() == ca.name, ca.get_fields()))),
            lambda ca: str(get_field_counter(ca)),
            get_method_set
        ]
        for ca in self.r_cas:
            c = ca.name
            if c.startswith("Lcom/") and self.dx2.get_class_analysis(c) is not None:
                candidates[c].add(c)
                continue

            for ca2 in self.dx2.get_classes():
                for cr in criteria:
                    if cr(ca) != cr(ca2):
                        break
                else:
                    candidates[c].add(str(ca2.name))

        return candidates


def get_field_counter(ca):
    li = []
    for f in map(FieldAnalysis.get_field, ca.get_fields()):
        if ca.name != f.get_class_name():
            continue

        li.append(get_usable(str(f.get_descriptor())))
    return Counter(li)


def get_method_set(ca):
    return {get_usable_description(m) for m in ca.get_methods()}
