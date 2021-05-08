from ._base import EnergyModelBase
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
                    ave_power = 0
                    for activity_i, activity_w in enumerate(self.human_data.weights):
                        activity_w = float(activity_w)
                        des_torque, des_angle, time_series, time_step = self.load_human_data(activity_i)
                        motor_behavior = self.actuator.backward_calculation_4qci(stiffness=stiffness,
                                                                                 ratio=ratio,
                                                                                 motor_inertia=m_inertia,
                                                                                 des_torque=des_torque,
                                                                                 des_angle=des_angle,
                                                                                 time_series=time_series)
                        motor_angle, motor_speed, motor_torque, actual_motor_eff = motor_behavior

                        mechanical_power = motor_speed / 60 * np.pi * motor_torque  # speed (rpm) to (rad/s)
                        electrical_power = mechanical_power / actual_motor_eff
                        # mechanical_energy = np.sum(mechanical_power) * time_step
                        electrical_power = np.clip(electrical_power, a_min=0, a_max=None)   # no-rechargable bettery
                        electrical_energy = np.sum(electrical_power) * time_step  # depend on direction of power flow
                        sum_energy += electrical_energy * activity_w
                        ave_power += np.mean(electrical_power) * activity_w

                    comb_info = {"energy": sum_energy, "ave_power": ave_power, "stiffness": stiffness, "ratio": ratio, "m_inertia": m_inertia}
                    all_comb_info.append(comb_info)

        # TODO: output max mechanical power to limit gear load
        ranked_comb_info = sorted(all_comb_info, key=lambda x: x["energy"])
        return ranked_comb_info

    def get_recommendation(self, ranked_comb_info, n_points=100):
        """
        From the top n_points, recommend optimal variables range
        """
        # TODO: Consider multiple local maxima
        top_comb_info = ranked_comb_info[:n_points]
        all_stiffness = sorted([x["stiffness"] for x in top_comb_info])
        all_ratio = sorted([x["ratio"] for x in top_comb_info])
        all_m_inertia = sorted([x["m_inertia"] for x in top_comb_info])

        stiffness_range = self._get_range(all_stiffness, self.params.stiffness_interval)
        ratio_range = self._get_range(all_ratio, self.params.gear_ratio_interval)
        m_inertia_range = self._get_range(all_m_inertia, self.params.motor_j_interval)

        return stiffness_range, ratio_range, m_inertia_range

    @staticmethod
    def _get_range(sources, interval):
        """
        Get optimal ranges from optimal set of numbers
        """
        # e.g. sourcee = [1,2,3, 5,6,7]
        param_range = []  # [[1,2,3], [5,6,7]] interval = 1
        subset_temp = []
        for i, x in enumerate(sources):
            subset_temp.append(x)
            if i+1 == len(sources) or sources[i + 1] - sources[i] > interval:
                param_range.append(subset_temp)
                subset_temp = []
        # final_range = [[1,3], [5,7]]
        final_range = [[x[0], x[-1]] for x in param_range]
        return final_range

    def get_peak_torque(self):
        peak_torque = 0
        for activity_i, activity_w in enumerate(self.human_data.weights):
            des_torque, des_angle, time_series, time_step = self.load_human_data(activity_i)
            peak_torque = max(max(des_torque), peak_torque)
        return peak_torque