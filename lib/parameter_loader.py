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
