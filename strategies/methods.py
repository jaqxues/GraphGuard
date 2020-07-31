from androguard.core.analysis.analysis import MethodAnalysis

from strategies.strategy import Strategy
from utils.formats import get_usable_description, pretty_format_ma

MIN_MATCH_POINTS = 2

cfs = (
    (get_usable_description, 10),
    (MethodAnalysis.get_access_flags_string, 4),
    (MethodAnalysis.get_length, 1),
    (lambda x: len(x.get_xref_to()), 1),
    (lambda x: len(x.get_xref_from()), 1)
)
total_score = sum((score for _, score in cfs))


class MethodStrategy(Strategy):
    def try_resolve_ms(self, matching_cs, exact):
        c_names = {str(ca.name) for ca in self.r_cas}
        min_points = total_score if exact else MIN_MATCH_POINTS

        candidates = {}
        for ma in self.r_mas:
            if ma.class_name in c_names:
                print("Class not resolve Class for Method", pretty_format_ma(ma))
                continue

            c_name1 = str(ma.class_name)
            c_name2 = matching_cs[c_name1]

            m_match_points = {}

            for ma2 in self.dx2.get_class_analysis(c_name2).get_methods():
                x = sum(((c_fun(ma) == c_fun(ma2)) * score for c_fun, score in cfs))
                if x >= min_points:
                    m_match_points[ma2] = x

            if m_match_points:
                max_matches = max(map(lambda x: x[1], m_match_points.items()))
                candidates[ma] = {ma for ma, score in m_match_points.items() if score == max_matches}

        return candidates
