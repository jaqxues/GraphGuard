FLAG_CLASS = 0b1
FLAG_METHOD = 0b10
FLAG_FIELD = 0b100


class StrategyHandler:
    def __init__(self):
        self.strategies = []
        self.new_idx = 0

    def add_strategy(self, apply_strategy, flags):
        self.new_idx = len(self.strategies)
        self.strategies.append((flags, apply_strategy))

    def invoke_strategies(self, r_cas=tuple(), r_mas=tuple(), r_fas=tuple(), only_new=False):
        flags = 0
        if r_cas:
            flags |= FLAG_CLASS
        if r_mas:
            flags |= FLAG_METHOD
        if r_fas:
            flags |= FLAG_FIELD

        if only_new:
            s_idx = self.new_idx
        else:
            s_idx = 0
        for idx, (flag, strategy) in enumerate(self.strategies):
            if (s_idx > idx) or (flags & flag == 0):
                continue

            strategy(r_cas, r_mas, r_fas)
