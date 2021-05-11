import importlib


class Params():
    """
    Load default or user defined parameters
    """

    def __init__(self, choice):
        if choice == "default":
            self._load_params("inputs.default_inputs")
        elif choice == "user_defined":
            self._load_params("inputs.user_inputs")

    def _load_params(self, module_name):
        pkg = importlib.import_module(module_name)
        self.stiffness_lower = pkg.STIFFNESS_LOWER
        self.stiffness_upper = pkg.STIFFNESS_UPPER
        self.stiffness_interval = pkg.STIFFNESS_INTERVAL
        self.gear_eff_c = pkg.GEAR_EFFICIENCY_CONSTANT
        self.motor_eff_c = pkg.MOTOR_EFFICIENCY_CONSTANT
        self.gear_ratio_lower = pkg.GEAR_RATIO_LOWER
        self.gear_ratio_upper = pkg.GEAR_RATIO_UPPER
        self.gear_ratio_interval = pkg.GEAR_RATIO_INTERVAL
        self.motor_j_lower = int(pkg.MOTOR_INERTIA_LOWER + pkg.LINK_INERTIA / pkg.GEAR_RATIO_UPPER ** 2)
        self.motor_j_upper = int(pkg.MOTOR_INERTIA_UPPER + pkg.LINK_INERTIA / pkg.GEAR_RATIO_UPPER ** 2)
        self.motor_j_interval = pkg.MOTOR_INERTIA_INTERVAL
        self.v_limit = pkg.DRIVER_VOLTAGE_LIMIT
        self.c_limit = pkg.DRIVER_CURRENT_LIMIT
        self.body_weight = pkg.BODY_WEIGHT
        self.link_inertia = pkg.LINK_INERTIA
        self.num_combs = sum([(self.stiffness_upper - self.stiffness_lower) / self.stiffness_interval,
                              (self.gear_ratio_upper - self.gear_ratio_lower) / self.gear_ratio_interval,
                              (self.motor_j_upper - self.motor_j_lower) / self.motor_j_interval])
        self.subopt_n = int(pkg.SUB_OPT_RATE * self.num_combs)


