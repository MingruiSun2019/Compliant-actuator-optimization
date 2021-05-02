from _base import EnergyModelBase
import numpy as np


class Optimize4QCI(EnergyModelBase):
    def __init__(self, human_data, actuator, params):
        super().__init__(human_data, actuator)
        self.params = params

    def optimize_routine(self):
        stiffness_iter = range(self.params.stiffness_lower, self.params.stiffness_upper, self.params.stiffness_interval)
        ratio_iter = range(self.params.gear_ratio_lower, self.params.gear_ratio_upper, self.params.gear_ratio_interval)
        motor_inertia_iter = range(self.params.motor_j_lower, self.params.motor_j_upper, self.params.motor_j_interval)

        all_comb_info = []   # electrical energy of all combinations
        for stiffness in stiffness_iter:
            for ratio in ratio_iter:
                for m_inertia in motor_inertia_iter:
                    sum_energy = 0   # sum of electrical energy over all activities
                    for activity_w, activity_i in enumerate(self.huaman_data.weights):
                        des_torque, des_angle, time_series, time_step = self.load_human_data(activity_i)
                        motor_behavior = self.actuator.backward_calculation_4qci(stiffness=stiffness,
                                                                                 ratio=ratio,
                                                                                 motor_inertia=m_inertia,
                                                                                 des_torque=des_torque,
                                                                                 des_angle=des_angle,
                                                                                 time_series=time_series)
                        motor_angle, motor_speed, motor_torque, actual_motor_eff = motor_behavior

                        mechanical_power = motor_speed / 60 * np.pi * motor_torque  # speed (rpm) to (rad/s)
                        mechanical_energy = np.sum(mechanical_power) * time_step
                        electrical_energy = mechanical_energy * actual_motor_eff  # depend on direction of power flow
                        sum_energy += electrical_energy * activity_w

                    comb_info = {"energy": sum_energy, "stiffness": stiffness, "ratio": ratio, "m_inertia": m_inertia}
                    all_comb_info.append(comb_info)

        ranked_comb_info = sorted(all_comb_info, key=lambda x: x["energy"])
        return ranked_comb_info

    @staticmethod
    def get_recommendation(ranked_comb_info, n_points=100):
        """
        From the top n_points, recommend optimal variables range
        """
        # TODO: Consider multiple local maxima
        top_comb_info = ranked_comb_info[:n_points]
        all_stiffness = sorted([x["stiffness"] for x in top_comb_info])
        all_ratio = sorted([x["ratio"] for x in top_comb_info])
        all_m_inertia = sorted([x["m_inertia"] for x in top_comb_info])

        stiffness_range = [all_stiffness[0], all_stiffness[-1]]
        ratio_range = [all_ratio[0], all_ratio[-1]]
        m_inertia_range = [all_m_inertia[0], all_m_inertia[-1]]

        return stiffness_range, ratio_range, m_inertia_range
