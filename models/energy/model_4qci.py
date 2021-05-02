class OptimizeBase():
    def __init__(self, params):
        self.params = params

    def optimize_routine(self):
        stiffness_iter = range(self.params.stiffness_lower, self.params.stiffness_upper, self.params.stiffness_interval)
        ratio_iter = range(self.params.gear_ratio_lower, self.params.gear_ratio_upper, self.params.gear_ratio_interval)
        for stiffness in stiffness_iter:
            for ratio in ratio_iter:
                pass
