import os
from ._base import ActuatorBase as BaseModel
import numpy as np


class SeaType1(BaseModel):
    """
    Motor -> Gear -> Spring -> output
    """

    def __init__(self, params, polyfitor, des_torque, des_angle, time_series, stiffness, ratio, motor_inertia):
        super().__init__(params, polyfitor, des_torque, des_angle, time_series)
        self.stiffness = stiffness * np.pi / 180   # Nm/deg
        self.ratio = ratio
        self.motor_inertia = motor_inertia

    def backward_calculation_4qci(self):
        """
        Calculate motor desired angle, speed, torque,
        given desired output angle, speed, torque
        """

        mid_angle = self.des_angle + self.des_torque / self.stiffness   # angle after gear
        spring_def_angle = self.des_angle - mid_angle

        motor_angle = mid_angle * self.ratio  # (deg)
        motor_speed = np.diff(motor_angle) / self.time_step * 60 / 360  # (rpm)
        motor_speed = np.append(motor_speed, motor_speed[-1])

        # Calculate motor acceleration by poly fit motor angle and double differentiate, so that no noise be introduced
        motor_angle_rad = motor_angle * np.pi / 180  # (rad)
        result_x, result_y = self.polyfitor.multi_fit(self.time_series, motor_angle_rad, self.time_series,
                                                      result_x=[], result_y=[])
        _, actual_motor_acc = self.polyfitor.get_acc(result_x, result_y)

        acc_torque = self.motor_inertia / 1e7 * actual_motor_acc  # torque for accelerate the rotor itself

        # HD_eff = get_hd_eff(hd, motor_speed)
        motor_torque = np.zeros(len(motor_speed))
        actual_motor_eff = np.zeros(len(motor_speed))
        for i in range(len(motor_speed)):
            if motor_speed[i] * self.des_torque[i] >= 0:
                actual_gear_eff = self.params.gear_eff_c
                actual_motor_eff[i] = self.params.motor_eff_c
            else:
                actual_gear_eff = 1 / self.params.gear_eff_c
                actual_motor_eff[i] = 1 / self.params.motor_eff_c
            motor_torque[i] = (self.des_torque[i] / self.ratio) / actual_gear_eff + acc_torque[i]

        return motor_angle, motor_speed, motor_torque, actual_motor_eff

    def forward_calculation(self):
        """
        Calculate actual output angle, speed, torque
        given actual motor angle, speed, torque
        """
        pass
