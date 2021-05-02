from _base import EnergyModelBase
import numpy as np


class OptimizeFMM(EnergyModelBase):
    def __init__(self, human_data, actuator, motor_catalog, gear_catalog):
        super().__init__(human_data, actuator)
        self.motor_catalog = motor_catalog
        self.gear_catalog = gear_catalog

    def optimize_routine(self, stiff_range):
        stiffness_iter = range(stiff_range[0], stiff_range[1], int((stiff_range[1] - stiff_range[0]) / 10))

        all_comb_info = []  # electrical energy of all combinations
        for stiffness in stiffness_iter:
            for gear_i, gear in self.gear_catalog.iterrows():
                for motor_i, motor in self.motor_catalog.iterrows():
                    sum_energy = 0  # sum of electrical energy over all activities
                    for activity_w, activity_i in enumerate(self.huaman_data.weights):
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

                        # TODO: do forward calculation, get performance rating, adding to comb_info

                    comb_info = {"energy": sum_energy, "stiffness": stiffness, "ratio": gear['ratio'],
                                 "m_inertia": motor['Jr']}
                    all_comb_info.append(comb_info)

        ranked_comb_info = sorted(all_comb_info, key=lambda x: x["energy"])
        return ranked_comb_info
