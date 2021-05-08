import os
from ._base import ActuatorBase as BaseModel
import numpy as np
from lib.utils import sigmoid


class SeaType1(BaseModel):
    """
    Motor -> Gear -> Spring -> output
    """

    def __init__(self, params, polyfitor, motor_eff_model):
        super().__init__(params, polyfitor, motor_eff_model)

    def _get_motor_behavior(self, stiffness, ratio, des_torque, des_angle, time_series):
        stiffness = stiffness * np.pi / 180  # Nm/deg
        time_step = time_series[1] - time_series[0]

        mid_angle = des_angle + des_torque / stiffness  # angle after gear
        spring_def_angle = des_angle - mid_angle

        motor_angle = mid_angle * ratio  # (deg)
        motor_speed = np.diff(motor_angle) / time_step * 60 / 360  # (rpm)
        motor_speed = np.append(motor_speed, motor_speed[-1])

        # Calculate motor acceleration by poly fit motor angle and double differentiate, so that no noise be introduced
        motor_angle_rad = motor_angle * np.pi / 180  # (rad)
        result_x, result_y = self.polyfitor.multi_fit(time_series, motor_angle_rad, time_series,
                                                      result_x=[], result_y=[])
        _, motor_acc = self.polyfitor.get_acc(result_x, result_y)

        self.time_series = time_series
        self.des_output_torque = des_torque
        self.des_motor_speed = motor_speed

        return motor_angle, motor_speed, motor_acc



