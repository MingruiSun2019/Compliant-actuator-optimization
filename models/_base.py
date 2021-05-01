import os


def ActuatorBase():
    """
    Explain base here
    """

    def __init__(self, temperature):
        self.temperature = temperature

    @property
    def spring_k(self):
        return self._spring_k

    @property.setter
    def spring_k(self, value):
        self._spring_k = max(1, value)
