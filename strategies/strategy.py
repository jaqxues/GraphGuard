from utils.formats import pretty_format_ma
from androguard.core.bytecode import FormatClassToJava


class Strategy:
    def __init__(self, dx, dx2, r_cas, r_mas, r_fas, accumulator):
        """
        :param accumulator: Used to filter out already matched declarations
        """
        self.dx = dx
        self.dx2 = dx2
        self.r_cas = accumulator.get_unmatched_cs(r_cas)
        self.r_mas = accumulator.get_unmatched_ms(r_mas)
        self.r_fas = accumulator.get_unmatched_fs(r_fas)
