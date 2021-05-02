import os
from ._base import ActuatorBase as BaseModel
import numpy as np


class SeaType1(BaseModel):
    """
    Motor -> Gear -> Spring -> output
    """

    def __init__(self, params, polyfitor):
        super().__init__(params, polyfitor)
        # TODO: put actual gear motor here

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
        return motor_angle, motor_speed, motor_acc

    def backward_calculation_4qci(self, stiffness, ratio, motor_inertia, des_torque, des_angle, time_series):
        """
        Calculate motor desired angle, speed, torque,
        given desired output angle, speed, torque
        """
        motor_angle, motor_speed, motor_acc = self._get_motor_behavior(stiffness, ratio,
                                                                       des_torque, des_angle, time_series)

        acc_torque = motor_inertia / 1e7 * motor_acc  # torque for accelerate the rotor itself

        # HD_eff = get_hd_eff(hd, motor_speed)
        motor_torque = np.zeros(len(motor_speed))
        actual_motor_eff = np.zeros(len(motor_speed))
        for i in range(len(motor_speed)):
            if motor_speed[i] * des_torque[i] >= 0:
                actual_gear_eff = self.params.gear_eff_c
                actual_motor_eff[i] = self.params.motor_eff_c
            else:
                actual_gear_eff = 1 / self.params.gear_eff_c
                actual_motor_eff[i] = 1 / self.params.motor_eff_c
            motor_torque[i] = (des_torque[i] / ratio) / actual_gear_eff + acc_torque[i]

        return motor_angle, motor_speed, motor_torque, actual_motor_eff

    def backward_calculation_fmm(self, stiffness, gear, motor, des_torque, des_angle, time_series):
        """
        Calculate motor desired angle, speed, torque,
        given desired output angle, speed, torque
        """
        # Read component parameters
        ratio, gear_eff, gear_inertia = gear['ratio'], gear['eff'], gear['inertia']
        motor_inertia, friction_torque = motor['Jr'], motor['Mr']

        motor_angle, motor_speed, motor_acc = self._get_motor_behavior(stiffness, ratio,
                                                                       des_torque, des_angle, time_series)

        acc_torque = (motor_inertia + gear_inertia) / 1e7 * motor_acc  # torque for accelerate the rotor itself

        # HD_eff = get_hd_eff(hd, motor_speed)
        motor_torque = np.zeros(len(motor_speed))
        for i in range(len(motor_speed)):
            if motor_speed[i] * des_torque[i] >= 0:
                actual_gear_eff = gear_eff
            else:
                actual_gear_eff = 1 / self.params.gear_eff_c
            motor_torque[i] = (des_torque[i] / ratio) / actual_gear_eff + acc_torque[i] + friction_torque

        return motor_angle, motor_speed, motor_torque

    def apply_voltage_current_limit(self, motor_torque, motor_speed, motor):
        windingR = motor['Rw']
        torque_constant = motor['km']
        speed_constant = motor['kn']
        torque_limit = torque_constant * self.params.c_limit
        speed_limit_0 = speed_constant * self.params.v_limit  # don't consider joule loss

        actual_motor_torque = np.clip(motor_torque, a_min=-torque_limit, a_max=torque_limit)

        temp_k = 30000 / np.pi * windingR / ((torque_constant * 1000) ** 2)  # motor gradient
        speed_limit = np.zeros(len(motor_speed))  # do consider joule loss
        for i in range(len(motor_speed)):
            speed_limit[i] = max(speed_limit_0 - temp_k * (np.abs(motor_torque[i]) * 1000), 0)

        actual_motor_speed = np.clip(motor_speed, a_min=-speed_limit, a_max=speed_limit)

        return actual_motor_torque, actual_motor_speed

    def get_motor_inputs(self, actual_motor_torque, actual_motor_speed, motor):
        # TODO: torque_limit other thins
        torque_constant = motor['km']
        speed_constant = motor['kn']
        windingR = motor['Rw']
        temp_k = 30000 / np.pi * windingR / ((torque_constant * 1000) ** 2)  # motor gradient
        input_current = np.clip(actual_motor_torque / torque_constant,
                                a_min=-self.params.c_limit, a_max=self.params.c_limit)
        input_voltage = np.clip((actual_motor_speed + temp_k * actual_motor_torque * 1000) / speed_constant,
                                a_min=-self.params.v_limit, a_max=self.params.v_limit)
        return input_voltage, input_current

    def forward_calculation(self):
        """
        Calculate actual output angle, speed, torque
        given actual motor angle, speed, torque
        """
        pass
