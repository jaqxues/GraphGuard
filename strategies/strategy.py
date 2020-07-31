from utils.formats import pretty_format_ma
from androguard.core.bytecode import FormatClassToJava


class Strategy:
    def __init__(self, dx, dx2, r_cas, r_mas, r_fas, accumulator):
        """
        :param accumulator: Used to filter out already matched declarations
        """
        self.dx = dx
        self.dx2 = dx2
        self.r_cas = r_cas
        self.r_mas = r_mas
        self.r_fas = r_fas
        self.accumulator = accumulator
        self.update_matched()

    def update_matched(self):
        self.r_cas = self.accumulator.get_unmatched_cs(self.r_cas)
        self.r_mas = self.accumulator.get_unmatched_ms(self.r_mas)
        self.r_fas = self.accumulator.get_unmatched_fs(self.r_fas)
