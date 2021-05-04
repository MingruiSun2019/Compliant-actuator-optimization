from ._base import EnergyModelBase
import numpy as np


class OptimizeFMM(EnergyModelBase):
    def __init__(self, human_data, actuator, stiff_range, motor_catalog, gear_catalog):
        super().__init__(human_data, actuator)
        self.stiff_range = stiff_range
        self.motor_catalog = motor_catalog
        self.gear_catalog = gear_catalog

    def optimize_routine(self):
        stiffness_iter = range(self.stiff_range[0], self.stiff_range[1], int((self.stiff_range[1] - self.stiff_range[0]) / 10))

        all_comb_info = []  # electrical energy of all combinations
        for stiffness in stiffness_iter:
            for gear_i, gear in self.gear_catalog.iterrows():
                for motor_i, motor in self.motor_catalog.iterrows():
                    sum_energy = 0  # sum of electrical energy over all activities
                    sum_torque_rating = 0
                    sum_speed_rating = 0
                    for activity_i, activity_w in enumerate(self.human_data.weights):
                        activity_w = float(activity_w)
                        des_torque, des_angle, time_series, time_step = self.load_human_data(activity_i)
                        motor_behavior = self.actuator.backward_calculation_fmm(stiffness=stiffness,
                                                                                gear=gear,
                                                                                motor=motor,
                                                                                des_torque=des_torque,
                                                                                des_angle=des_angle,
                                                                                time_series=time_series)
                        motor_angle, motor_speed, motor_torque = motor_behavior
                        actual_motor_torque, actual_motor_speed = self.actuator.apply_voltage_current_limit(motor_torque, motor_speed, motor)
                        input_voltage, input_current = self.actuator.get_motor_inputs(actual_motor_torque, actual_motor_speed, motor)

                        electrical_power = input_voltage * input_current  # speed (rpm) to (rad/s)
                        electrical_energy = np.sum(electrical_power) * time_step
                        sum_energy += electrical_energy * activity_w

                        # Forward calculation and performance rating
                        actual_output_torque = self.actuator.forward_calculation(actual_motor_torque, gear, motor)
                        torque_rating, speed_rating = self.actuator.get_performance_rating(actual_output_torque, actual_motor_speed, des_torque)
                        sum_torque_rating += torque_rating * activity_w
                        sum_speed_rating += speed_rating * activity_w

                    ave_torque_rating = sum_torque_rating / np.sum(self.human_data.weights)
                    ave_speed_rating = sum_speed_rating / np.sum(self.human_data.weights)
                    # TODO: spring angle can be one
                    comb_info = {"energy": sum_energy, "stiffness": stiffness, "gear_id": gear['ID'],
                                 "motor_id": motor['ID'], "T_rating": ave_torque_rating, "V_rating": ave_speed_rating}
                    all_comb_info.append(comb_info)

        ranked_comb_info = sorted(all_comb_info, key=lambda x: x["energy"])
        return ranked_comb_info
