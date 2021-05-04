import os
from ._base import ActuatorBase as BaseModel
import numpy as np

print(type(BaseModel))
class SeaType1(BaseModel):
    """
    Motor -> Gear -> Spring -> output
    """

    def __init__(self, params, polyfitor):
        super().__init__(params, polyfitor)
        self._acc_torque = None
        self.des_motor_speed = None  # done
        self.des_motor_torque = None  # done
        self.actual_motor_speed = None  # done
        self.actual_motor_torque = None  # done
        self.des_output_torque = None  # done
        self.actual_output_torque = None  # done
        self._actual_gear_eff = None
        self.input_voltage = None  # done
        self.input_current = None  # done
        self.mechanical_power = None
        self.electrical_power = None
        self.time_series = None

    def initialize(self):
        self._acc_torque = None
        self.des_motor_speed = None  # done
        self.des_motor_torque = None  # done
        self.actual_motor_speed = None  # done
        self.actual_motor_torque = None  # done
        self.des_output_torque = None  # done
        self.actual_output_torque = None  # done
        self._actual_gear_eff = None
        self.input_voltage = None  # done
        self.input_current = None  # done
        self.mechanical_power = None
        self.electrical_power = None
        self.time_series = None

    def _get_motor_behavior(self, stiffness, ratio, des_torque, des_angle, time_series):
        self.time_series = time_series
        self.des_output_torque = des_torque
        stiffness = stiffness * np.pi / 180  # Nm/deg
        time_step = time_series[1] - time_series[0]

        mid_angle = des_angle + des_torque / stiffness  # angle after gear
        spring_def_angle = des_angle - mid_angle

        motor_angle = mid_angle * ratio  # (deg)
        motor_speed = np.diff(motor_angle) / time_step * 60 / 360  # (rpm)
        motor_speed = np.append(motor_speed, motor_speed[-1])
        self.des_motor_speed = motor_speed

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

        self.des_motor_torque = motor_torque
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
        self._acc_torque = acc_torque

        # HD_eff = get_hd_eff(hd, motor_speed)
        self._actual_gear_eff = np.zeros(len(motor_speed))
        for i in range(len(motor_speed)):
            if motor_speed[i] * des_torque[i] >= 0:
                self._actual_gear_eff[i] = gear_eff
            else:
                self._actual_gear_eff[i] = 1 / self.params.gear_eff_c
        motor_torque = (des_torque / ratio) / self._actual_gear_eff + acc_torque + friction_torque
        self.des_motor_torque = motor_torque
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

        self.actual_motor_speed = actual_motor_speed
        self.actual_motor_torque = actual_motor_torque
        return actual_motor_torque, actual_motor_speed

    def get_motor_inputs(self, actual_motor_torque, actual_motor_speed, motor):
        torque_constant = motor['km']
        speed_constant = motor['kn']
        windingR = motor['Rw']
        temp_k = 30000 / np.pi * windingR / ((torque_constant * 1000) ** 2)  # motor gradient
        input_current = np.clip(actual_motor_torque / torque_constant,
                                a_min=-self.params.c_limit, a_max=self.params.c_limit)
        input_voltage = np.clip((actual_motor_speed + temp_k * actual_motor_torque * 1000) / speed_constant,
                                a_min=-self.params.v_limit, a_max=self.params.v_limit)
        self.input_current = input_current
        self.input_voltage = input_voltage
        return input_voltage, input_current

    def forward_calculation(self, actual_motor_torque, gear, motor):
        """
        Calculate actual output angle, speed, torque
        given actual motor angle, speed, torque
        """
        ratio = gear['ratio']
        friction_torque = motor['Mr']
        actual_output_torque = (actual_motor_torque - self._acc_torque - friction_torque) * ratio * self._actual_gear_eff
        self.actual_output_torque = actual_output_torque
        return actual_output_torque

    def get_performance_rating(self, actual_output_torque, actual_motor_speed, des_output_torque):
        max_des_torque = np.max(des_output_torque)
        max_torque_deviation = max_des_torque * 0.02
        max_des_motor_speed = np.max(self.des_motor_speed)
        max_speed_deviation = max_des_motor_speed * 0.02
        data_len = len(des_output_torque)
        torque_rating = np.sum(np.abs(actual_output_torque-des_output_torque) < max_torque_deviation) / data_len   # 0-1, higher better
        speed_rating = np.sum(np.abs(actual_motor_speed-self.des_motor_speed) < max_speed_deviation) / data_len   # 0-1, higher better
        # TODO: UI rating

        return torque_rating, speed_rating

    def get_powers(self):
        """
        Get mechanical power and electrical power
        """
        self.mechanical_power = self.actual_motor_torque * self.actual_motor_speed / 60 * np.pi
        self.electrical_power = self.input_voltage * self.input_current

    def gather_info(self, stiffness, gear, motor, des_torque, des_angle, time_series):
        motor_angle, motor_speed, motor_torque = self.backward_calculation_fmm(stiffness, gear, motor, des_torque, des_angle, time_series)
        actual_motor_torque, actual_motor_speed = self.apply_voltage_current_limit(motor_torque, motor_speed, motor)
        input_voltage, input_current = self.get_motor_inputs(actual_motor_torque, actual_motor_speed, motor)
        actual_output_torque = self.forward_calculation(actual_motor_torque, gear, motor)
        self.get_powers()


