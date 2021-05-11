from ._base import EnergyModelBase
import numpy as np


class OptimizeFMM(EnergyModelBase):
    def __init__(self, human_data, actuator, stiff_range, motor_catalog, gear_catalog):
        super().__init__(human_data, actuator)
        self.stiff_range = stiff_range
        self.motor_catalog = motor_catalog
        self.gear_catalog = gear_catalog

    def optimize_routine(self):
        stiffness_iter = self._get_iter_from_range(self.stiff_range, n_points=3)

        all_comb_info = []  # electrical energy of all combinations
        for stiffness in stiffness_iter:
            for gear_i, gear in self.gear_catalog.iterrows():
                for motor_i, motor in self.motor_catalog.iterrows():
                    sum_energy = 0  # sum of electrical energy over all activities
                    sum_torque_rating, sum_speed_rating, sum_current_rating, sum_voltage_rating = 0, 0, 0, 0
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

                        # electrical_power = input_voltage * input_current  # speed (rpm) to (rad/s)
                        electrical_power = np.array(len(motor_speed))
                        for i in range(len(motor_speed)):
                            if motor_speed[i] * des_torque[i] >= 0:
                                electrical_power = motor_speed / 60 * 2 * np.pi * motor_torque + motor["Rw"] * input_current ** 2
                            else:
                                electrical_power = motor_speed / 60 * 2 * np.pi * motor_torque - motor["Rw"] * input_current ** 2

                        electrical_power = np.clip(electrical_power, a_min=0, a_max=None)  # no-rechargable bettery
                        electrical_energy = np.sum(electrical_power) * time_step
                        sum_energy += electrical_energy * activity_w

                        # Forward calculation and performance rating
                        _ = self.actuator.forward_calculation(actual_motor_torque, gear, motor)
                        torque_rating, speed_rating, current_rating, voltage_rating = self.actuator.get_performance_rating(motor)
                        sum_torque_rating += torque_rating * activity_w
                        sum_speed_rating += speed_rating * activity_w
                        sum_current_rating += current_rating * activity_w
                        sum_voltage_rating += voltage_rating * activity_w

                    ave_torque_rating = sum_torque_rating / np.sum(self.human_data.weights)
                    ave_speed_rating = sum_speed_rating / np.sum(self.human_data.weights)
                    ave_current_rating = sum_current_rating / np.sum(self.human_data.weights)
                    ave_voltage_rating = sum_voltage_rating / np.sum(self.human_data.weights)
                    # TODO: spring angle can be one
                    comb_info = {"energy": sum_energy, "stiffness": stiffness, "gear_name": gear['Name'],
                                 "motor_name": motor['Name'], "T_rating": ave_torque_rating, "V_rating": ave_speed_rating,
                                 "U_rating": ave_voltage_rating, "I_rating": ave_current_rating,
                                 "motor_dia": motor["diameter"], "motor_length": motor["length"], "gear_type": gear["type"]}
                    all_comb_info.append(comb_info)

        ranked_comb_info = sorted(all_comb_info, key=lambda x: x["energy"])
        max_ratings = self._get_max_rating(ranked_comb_info)
        return ranked_comb_info, max_ratings

    @staticmethod
    def _get_iter_from_range(source, n_points):
        # n_points in each subset
        output_iter = []
        for sub_range in source:
            if sub_range[0] == sub_range[1]:
                output_iter += [sub_range[0]]
            else:
                inter = max(int(np.floor((sub_range[1] - sub_range[0]) / n_points)), 1)
                output_iter += list(range(sub_range[0], sub_range[1], inter))
        return output_iter

    @staticmethod
    def _get_max_rating(all_comb_info):
        max_torque_rating = max([x["T_rating"] for x in all_comb_info])
        max_speed_rating = max([x["V_rating"] for x in all_comb_info])
        max_current_rating = max([x["U_rating"] for x in all_comb_info])
        max_voltage_rating = max([x["I_rating"] for x in all_comb_info])

        max_ratings = {"T_rating": max_torque_rating,
                       "V_rating": max_speed_rating,
                       "I_rating": max_current_rating,
                       "U_rating": max_voltage_rating}

        return max_ratings
