import os
from ._base import ActuatorBase as BaseModel


class SeaType1(BaseModel):
    """
    Explain
    """

    def __init__(self):
        super().__init__(*args, **kwargs)
        pass

    def backward_calculation(self):
        """
        Calculate motor desired angle, speed, torque,
        given desired output angle, speed, torque
        """
        pass

    def forward_calculation(self):
        """
        Calculate actual output angle, speed, torque
        given actual motor angle, speed, torque
        """
        pass
