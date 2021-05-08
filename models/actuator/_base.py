import numpy as np
from lib.utils import sigmoid


class ActuatorBase():
    """
    Explain base here
    """

    def __init__(self, params, polyfitor, motor_eff_model):
        self.params = params
        self.polyfitor = polyfitor

        self.motor_eff_model = motor_eff_model
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
        return None, None, None

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
        # poly_coef = [0.00144497, -0.05156015, 0.60075288, -1.30124496]
        for i in range(len(motor_speed)):
            if motor_speed[i] * des_torque[i] >= 0:
                actual_gear_eff = self.params.gear_eff_c
            else:
                actual_gear_eff = 1 / self.params.gear_eff_c
            motor_torque[i] = (des_torque[i] / ratio) / actual_gear_eff + acc_torque[i]

        for i in range(len(motor_speed)):
            fitted_motor_eff = sigmoid(np.log(np.abs(motor_speed[i] / motor_torque[i])), *self.motor_eff_model)
            if motor_speed[i] * des_torque[i] >= 0:
                actual_motor_eff[i] = fitted_motor_eff
            else:
                actual_motor_eff[i] = 1 / fitted_motor_eff

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

        # TODO: HD_eff = get_hd_eff(hd, motor_speed)
        self._actual_gear_eff = np.zeros(len(motor_speed))
        for i in range(len(motor_speed)):
            if motor_speed[i] * des_torque[i] >= 0:
                self._actual_gear_eff[i] = gear_eff
            else:
                self._actual_gear_eff[i] = 1 / self.params.gear_eff_c
        motor_torque = (des_torque / ratio) / self._actual_gear_eff + acc_torque + friction_torque

        self._acc_torque = acc_torque
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

    def get_performance_rating(self, motor):
        nominal_current = motor["In"]
        nominal_voltage = motor["Vn"]

        torque_rating = np.sqrt(np.mean((self.actual_output_torque-self.des_output_torque)**2))   # RMSE
        speed_rating = np.sqrt(np.mean((self.actual_motor_speed - self.des_motor_speed) ** 2))   # RMSE

        current_rating = np.sqrt(np.sum(np.clip(np.abs(self.input_current) - np.abs(nominal_current), a_min=0, a_max=None) ** 2))
        voltage_rating = np.sqrt(np.sum(np.clip(np.abs(self.input_voltage) - np.abs(nominal_voltage), a_min=0, a_max=None) ** 2))

        return torque_rating, speed_rating, current_rating, voltage_rating

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
