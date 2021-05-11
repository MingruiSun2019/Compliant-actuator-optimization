"""
This file includes all other minor functions
"""
import pandas as pd
import numpy as np
import copy
from scipy.optimize import curve_fit


def ask_answer(question):
    """
    Get user inputs
    """
    print(question)
    ans = input()
    return ans


def load_catalog(filename):
    """
    Load Gear or Motor catalog
    """
    catalog = pd.read_csv(filename)
    return catalog


def sigmoid(x, L, x0, k, b):
    y = L / (1 + np.exp(-k * (x - x0))) + b
    return (y)


def fit_motor_efficiency(motor_catalog):
    motor_catalog = load_catalog(motor_catalog)
    speed_torque_ratio_data = []
    efficiency_data = []
    motor_count = 0
    for index, row in motor_catalog.iterrows():
        if motor_count > 10:
            break
        speed_array = np.linspace(100, row["Vn"] * row["kn"] * 1, 50)
        torque_array = np.linspace(0.05, row["In"] * row["km"] * 5, 50)
        t_s_ratio_array = np.zeros(len(speed_array) * len(torque_array))
        current_array = np.zeros(len(t_s_ratio_array))
        joule_array = np.zeros(len(t_s_ratio_array))
        pm_array = np.zeros(len(t_s_ratio_array))
        eff_list = np.zeros(len(t_s_ratio_array))
        count = 0
        for speed in speed_array:
            for torque in torque_array:
                t_s_ratio_array[count] = speed / torque
                current_array[count] = torque / row["km"]
                joule_array[count] = current_array[count] ** 2 * row["Rw"]
                pm_array[count] = speed * torque
                eff_list[count] = pm_array[count] / (pm_array[count] + joule_array[count])
                count += 1

        speed_torque_ratio_data += list(np.log(t_s_ratio_array))
        efficiency_data += list(eff_list)
        motor_count += 1

    p0 = [max(efficiency_data), np.median(speed_torque_ratio_data), 1, min(efficiency_data)]  # this is an mandatory initial guess
    popt, pcov = curve_fit(sigmoid, speed_torque_ratio_data, efficiency_data, p0, method='dogbox')

    return popt


def num_2dec(num):
    return "{:.2f}".format(num)


def narrow_down_motor_catalog(inertia_range, min_ave_power, filename):
    def_cat = load_catalog(filename)
    count = 0
    for sub_range in inertia_range:
        sub_cat = def_cat[(def_cat["Jr"] >= sub_range[0]-200) & (def_cat["Jr"] <= sub_range[1])]   # to include gear inertia

        if count == 0:
            filtered_cat = sub_cat
        else:
            pd.concat([filtered_cat, sub_cat])
        count += 1

    # Process when there is no gear between key_range
    if len(filtered_cat) == 0:
        new_inertia_range = copy.deepcopy(inertia_range)
        all_inertia = sorted(list(def_cat["Jr"]))
        for sub_i, sub_range in enumerate(inertia_range):
            for inertia in all_inertia:
                if inertia < sub_range[0]:
                    new_inertia_range[sub_i][0] = inertia
                else:
                    new_inertia_range[sub_i][1] = inertia
                    break
        filtered_cat = narrow_down_motor_catalog(new_inertia_range, min_ave_power, filename)
        filtered_cat.drop_duplicates()
    else:
        filtered_cat = filtered_cat[filtered_cat["Power"] >= min_ave_power]

    return filtered_cat


def narrow_down_gear_catalog(key_range, min_peak_torque, filename):
    def_cat = load_catalog(filename)
    count = 0
    for sub_range in key_range:
        sub_cat = def_cat[(def_cat["ratio"] >= sub_range[0]) & (def_cat["ratio"] <= sub_range[1])]
        if count == 0:
            filtered_cat = sub_cat
        else:
            pd.concat([filtered_cat, sub_cat])
        count += 1

    # Process when there is no gear between key_range
    if len(filtered_cat) == 0:
        new_key_range = copy.deepcopy(key_range)
        all_ratio = sorted(list(def_cat["ratio"]))
        for sub_i, sub_range in enumerate(key_range):
            for ratio in all_ratio:
                if ratio < sub_range[0]:
                    new_key_range[sub_i][0] = ratio
                else:
                    new_key_range[sub_i][1] = ratio
                    break
        filtered_cat = narrow_down_gear_catalog(new_key_range, min_peak_torque, filename)
        filtered_cat.drop_duplicates()
    else:
        filtered_cat = filtered_cat[filtered_cat["peak_torque"] >= min_peak_torque]

    return filtered_cat


def refine_inertia_range(m_inertia_range, gear_catalog, params):
    max_gear_inertia = max(gear_catalog["inertia"])
    min_gear_inertia = min(gear_catalog["inertia"])
    max_ratio = max(gear_catalog["ratio"])
    min_ratio = min(gear_catalog["ratio"])

    refined_inertia_range = []
    for sub_range in m_inertia_range:
        motor_inertia_min = sub_range[0] - max_gear_inertia - params.link_inertia / (min_ratio ** 2)
        motor_inertia_max = sub_range[1] - min_gear_inertia - params.link_inertia / (max_ratio ** 2)
        refined_inertia_range.append([motor_inertia_min, motor_inertia_max])

    return refined_inertia_range
