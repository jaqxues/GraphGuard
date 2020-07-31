from utils.formats import pretty_format_ma
from androguard.core.bytecode import FormatClassToJava


class Strategy:
    def __init__(self, dx, dx2, c_decs, r_cas, m_decs, r_mas, f_decs, r_fas, accumulator):
        """
        :param accumulator: Used to filter out already matched declarations
        """
        self.dx = dx
        self.dx2 = dx2
        self.c_decs = accumulator.get_unmatched_cs(c_decs)
        self.r_cas = r_cas
        self.m_decs = accumulator.get_unmatched_ms(m_decs)
        self.r_mas = r_mas
        self.f_decs = accumulator.get_unmatched_fs(f_decs)
        self.r_fas = r_fas
